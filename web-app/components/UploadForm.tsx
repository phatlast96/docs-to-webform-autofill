"use client";

import { useId, useState } from "react";
import { submitAutofill } from "@/services/api";
import type { AutofillResponse } from "@/services/types";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileDropZone({
  id,
  label,
  hint,
  accept,
  files,
  onChange,
}: {
  id: string;
  label: string;
  hint: string;
  accept: string;
  files: File[];
  onChange: (files: File[]) => void;
}) {
  const [dragging, setDragging] = useState(false);

  function handleFiles(list: FileList | null) {
    onChange(Array.from(list ?? []));
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between gap-3">
        <label htmlFor={id} className="text-sm font-semibold tracking-wide text-foreground">
          {label}
        </label>
        <span className="text-xs text-muted">{hint}</span>
      </div>

      <label
        htmlFor={id}
        onDragEnter={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setDragging(false);
        }}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={[
          "group relative flex cursor-pointer flex-col gap-3 rounded-2xl border border-dashed px-4 py-5 transition-all duration-200",
          "bg-surface hover:border-accent hover:bg-accent-soft/40",
          dragging
            ? "border-accent bg-accent-soft/50 scale-[1.01] shadow-[0_0_0_3px_rgba(15,92,76,0.12)]"
            : "border-border-strong",
        ].join(" ")}
      >
        <input
          id={id}
          type="file"
          accept={accept}
          multiple
          className="sr-only"
          onChange={(e) => handleFiles(e.target.files)}
        />

        <div className="flex items-center gap-3">
          <span
            aria-hidden
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-muted text-accent transition-colors group-hover:bg-accent-soft"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M12 16V4M12 4l-4 4M12 4l4 4" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M4 14v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4" strokeLinecap="round" />
            </svg>
          </span>
          <div className="min-w-0">
            <p className="text-sm font-medium text-foreground">
              Drop files here, or <span className="text-accent underline-offset-2 group-hover:underline">browse</span>
            </p>
            <p className="text-xs text-muted">Multiple files supported</p>
          </div>
        </div>

        {files.length > 0 && (
          <ul className="flex flex-col gap-1.5 border-t border-border pt-3">
            {files.map((file) => (
              <li
                key={`${file.name}-${file.size}-${file.lastModified}`}
                className="flex items-center justify-between gap-3 rounded-lg bg-surface-muted/70 px-3 py-2 text-sm"
              >
                <span className="truncate font-medium text-foreground">{file.name}</span>
                <span className="shrink-0 text-xs text-muted">{formatBytes(file.size)}</span>
              </li>
            ))}
          </ul>
        )}
      </label>
    </div>
  );
}

export default function UploadForm() {
  const imageId = useId();
  const pdfId = useId();
  const [useRawDocuments, setUseRawDocuments] = useState(false);
  const [images, setImages] = useState<File[]>([]);
  const [pdfs, setPdfs] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AutofillResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileCount = images.length + pdfs.length;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!images.length && !pdfs.length) {
      setError("Add at least one image or PDF to continue.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await submitAutofill(images, pdfs, useRawDocuments));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="animate-fade-up flex w-full flex-col gap-8 rounded-[28px] border border-border bg-surface/90 p-6 shadow-[0_24px_60px_-36px_rgba(28,25,23,0.45)] backdrop-blur-sm sm:p-8"
    >
      <header className="flex flex-col gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent">
          Docs → Web form
        </p>
        <h1 className="font-[family-name:var(--font-display)] text-4xl leading-[1.1] tracking-tight text-foreground sm:text-[2.75rem]">
          Document Autofill
        </h1>
        <p className="max-w-md text-base leading-relaxed text-muted">
          Upload passport images and G-28 PDFs. We extract the fields, map them with AI,
          and fill the target form for you.
        </p>
      </header>

      <section className="flex flex-col gap-5" aria-label="Document uploads">
        <FileDropZone
          id={imageId}
          label="Images"
          hint="Passport scans, photos"
          accept="image/*"
          files={images}
          onChange={setImages}
        />
        <FileDropZone
          id={pdfId}
          label="PDFs"
          hint="G-28 and related forms"
          accept="application/pdf"
          files={pdfs}
          onChange={setPdfs}
        />
      </section>

      <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-border bg-surface-muted/50 px-4 py-4 transition-colors hover:bg-surface-muted">
        <input
          type="checkbox"
          checked={useRawDocuments}
          onChange={(e) => setUseRawDocuments(e.target.checked)}
          className="mt-0.5 h-4 w-4 accent-accent"
        />
        <span className="flex flex-col gap-1">
          <span className="text-sm font-semibold text-foreground">
            Use raw documents in LLM (slower, more accurate)
          </span>
          <span className="text-sm leading-relaxed text-muted">
            Send original images and PDF pages directly to OpenAI vision.
            When off, documents are preprocessed with OCR and PDF text extraction first.
          </span>
        </span>
      </label>

      <div className="flex flex-col gap-3">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex h-12 items-center justify-center rounded-full bg-accent px-6 text-sm font-semibold tracking-wide text-white transition-colors duration-200 hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-55"
        >
          {loading ? (
            <span className="animate-pulse-soft">Extracting & filling form…</span>
          ) : (
            `Upload & Autofill${fileCount > 0 ? ` (${fileCount})` : ""}`
          )}
        </button>

        {error && (
          <p
            role="alert"
            className="animate-fade-up rounded-xl bg-danger-soft px-4 py-3 text-sm text-danger"
          >
            {error}
          </p>
        )}
      </div>

      {result && (
        <section
          aria-label="Autofill result"
          className="animate-fade-up flex flex-col gap-3 border-t border-border pt-6"
        >
          <div className="flex flex-wrap items-end justify-between gap-2">
            <div>
              <h2 className="font-[family-name:var(--font-display)] text-xl tracking-tight text-foreground">
                Result
              </h2>
              <p className="text-sm text-muted">
                {result.form_field_count} form fields ·{" "}
                {result.fill_result.filled.length} filled ·{" "}
                {result.fill_result.skipped.length} skipped ·{" "}
                {result.input_tokens.toLocaleString()} input tokens ·{" "}
                {result.output_tokens.toLocaleString()} output tokens
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div className="rounded-2xl bg-surface-muted px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-muted">Fields</p>
              <p className="mt-1 text-2xl font-semibold tabular-nums text-foreground">
                {result.form_field_count}
              </p>
            </div>
            <div className="rounded-2xl bg-accent-soft px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-accent">Filled</p>
              <p className="mt-1 text-2xl font-semibold tabular-nums text-accent">
                {result.fill_result.filled.length}
              </p>
            </div>
            <div className="col-span-2 rounded-2xl bg-surface-muted px-4 py-3 sm:col-span-1">
              <p className="text-xs uppercase tracking-wide text-muted">Skipped</p>
              <p className="mt-1 text-2xl font-semibold tabular-nums text-foreground">
                {result.fill_result.skipped.length}
              </p>
            </div>
          </div>

          <details className="group rounded-2xl border border-border bg-surface-muted/50 open:bg-surface">
            <summary className="cursor-pointer list-none px-4 py-3 text-sm font-medium text-foreground marker:content-none [&::-webkit-details-marker]:hidden">
              <span className="flex items-center justify-between gap-2">
                View raw response
                <span className="text-muted transition-transform group-open:rotate-180">▾</span>
              </span>
            </summary>
            <pre className="max-h-72 overflow-auto border-t border-border px-4 py-3 font-mono text-xs leading-relaxed text-muted">
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </section>
      )}
    </form>
  );
}
