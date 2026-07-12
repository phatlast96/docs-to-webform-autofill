import UploadForm from "@/components/UploadForm";

export default function Home() {
  return (
    <div className="relative flex flex-1 items-center justify-center overflow-hidden px-5 py-12 sm:px-8">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_#ffffff_0%,_transparent_55%),radial-gradient(ellipse_at_bottom_right,_#d5ebe4_0%,_transparent_42%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.3] [background-image:linear-gradient(to_right,rgba(168,184,177,0.22)_1px,transparent_1px),linear-gradient(to_bottom,rgba(168,184,177,0.22)_1px,transparent_1px)] [background-size:28px_28px] [mask-image:radial-gradient(ellipse_at_center,black_35%,transparent_80%)]"
      />
      <div className="relative z-10 w-full max-w-xl">
        <UploadForm />
      </div>
    </div>
  );
}
