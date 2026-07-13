import type { AutofillResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function submitAutofill(
  images: File[],
  pdfs: File[],
  useRawDocuments: boolean = false,
  formUrl?: string
): Promise<AutofillResponse> {
  const formData = new FormData();
  images.forEach((f) => formData.append("images", f));
  pdfs.forEach((f) => formData.append("pdfs", f));
  formData.append("use_raw_documents", String(useRawDocuments));
  if (formUrl) {
    formData.append("form_url", formUrl);
  }

  const res = await fetch(`${API_BASE}/autofill`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error((await res.text()) || `Request failed: ${res.status}`);
  }
  return res.json();
}
