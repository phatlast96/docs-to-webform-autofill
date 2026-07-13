import asyncio
import contextlib

from playwright.async_api import Page, async_playwright

from config import settings
from schemas.form_fields import FormField, FormSchema

JS_EXTRACT_FIELDS = """
() => {
  const results = [];
  const inputs = document.querySelectorAll('input, select, textarea');
  for (const el of inputs) {
    if (!el.name || el.type === 'hidden') continue;
    let label = '';
    const id = el.id;
    if (id) {
      const lbl = document.querySelector(`label[for="${id}"]`);
      if (lbl) label = lbl.textContent.trim();
    }
    if (!label) {
      const parent = el.closest('.form-row, .checkbox-group');
      if (parent) {
        const lbl = parent.querySelector('label');
        if (lbl) label = lbl.textContent.trim();
      }
    }
    const tag = el.tagName.toLowerCase();
    const type = tag === 'select' ? 'select' : el.type;
    const options = tag === 'select'
      ? [...el.options].map(o => o.value).filter(v => v)
      : (el.type === 'checkbox' && el.value ? [el.value] : []);
    results.push({ name: el.name, label, type, options, id });
  }
  return results;
}
"""


def _normalize_field_type(html_type: str, is_group: bool) -> str:
    if is_group and html_type == "checkbox":
        return "checkbox_group"
    if html_type == "select-one":
        return "select"
    return html_type


async def _headful_session_lifetime(p, browser, page: Page) -> None:
    """Keep playwright alive until the browser is closed, then clean up."""
    closed = asyncio.Event()
    page.on("close", lambda _: closed.set())
    browser.on("disconnected", lambda _: closed.set())

    async def _poll() -> None:
        while not closed.is_set():
            try:
                await page.title()
            except Exception:
                closed.set()
                return
            if page.is_closed() or not browser.is_connected():
                closed.set()
                return
            await asyncio.sleep(0.5)

    poll_task = asyncio.create_task(_poll())
    try:
        await closed.wait()
    finally:
        poll_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await poll_task
        if browser.is_connected():
            await browser.close()
        await p.stop()


async def extract_form_schema(url: str | None = None) -> FormSchema:
    url = url or settings.form_url
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not settings.playwright_headful)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        raw = await page.evaluate(JS_EXTRACT_FIELDS)
        await page.evaluate(
            "() => document.querySelectorAll('style').forEach(el => el.remove())"
        )
        page_html = await page.content()
        await browser.close()

    # Aggregate all checkbox values for each shared name into one option list
    checkbox_options: dict[str, list[str]] = {}
    for item in raw:
        if item["type"] != "checkbox":
            continue
        name = item["name"]
        checkbox_options.setdefault(name, [])
        for opt in item.get("options", []):
            if opt and opt not in checkbox_options[name]:
                checkbox_options[name].append(opt)

    seen_names: set[str] = set()
    fields: list[FormField] = []
    for item in raw:
        name, html_type = item["name"], item["type"]
        if name in seen_names:
            continue
        is_group = html_type == "checkbox" and len(checkbox_options.get(name, [])) > 0
        seen_names.add(name)
        options = (
            checkbox_options[name]
            if is_group
            else item.get("options", [])
        )
        fields.append(
            FormField(
                name=name,
                label=item["label"],
                field_type=_normalize_field_type(html_type, is_group),
                options=options,
            )
        )
    return FormSchema(url=url, fields=fields, page_html=page_html)


async def fill_form(
    data: dict[str, str | bool | None],
    url: str | None = None,
) -> dict:
    url = url or settings.form_url
    filled: list[str] = []
    skipped: list[str] = []
    p = await async_playwright().start()
    browser = await p.chromium.launch(
        headless=not settings.playwright_headful,
        slow_mo=200 if settings.playwright_headful else 0,
    )
    try:
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        for name, value in data.items():
            if value is None or value == "":
                skipped.append(name)
                continue
            try:
                await _fill_field(page, name, value)
                filled.append(name)
            except Exception as e:
                skipped.append(f"{name}:{e}")

        result = {"filled": filled, "skipped": skipped}
        if settings.playwright_headful:
            print(
                "Headful mode: filled form is open for inspection. "
                "Results are returned immediately; close the browser when done."
            )
            asyncio.create_task(_headful_session_lifetime(p, browser, page))
            return result

        await browser.close()
        await p.stop()
        return result
    except Exception:
        if browser.is_connected():
            await browser.close()
        await p.stop()
        raise


async def _fill_field(page: Page, name: str, value: str | bool) -> None:
    el = page.locator(f'[name="{name}"]').first
    tag = await el.evaluate("e => e.tagName.toLowerCase()")
    input_type = await el.evaluate("e => e.type")

    if input_type == "checkbox":
        if value is True or value == "true":
            await el.check()
        elif isinstance(value, str):
            await page.locator(f'[name="{name}"][value="{value}"]').check()
    elif tag == "select":
        await el.select_option(str(value))
    else:
        await el.fill(str(value))
