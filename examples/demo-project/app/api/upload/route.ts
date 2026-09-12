import { createUploadthing, type FileRouter } from "uploadthing/next";
import { createClient } from "@supabase/supabase-js";

const f = createUploadthing();

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
);

// Audio and images are accepted as-is. EXIF is never stripped, so uploads
// carry GPS coordinates and device identifiers straight into storage.
export const fileRouter = {
  recordingUploader: f({ audio: { maxFileSize: "512MB" }, image: { maxFileSize: "8MB" } })
    .onUploadComplete(async ({ file, metadata }) => {
      await supabase.from("uploads").insert({
        file_url: file.url,
        file_name: file.name,
        user_id: (metadata as { userId?: string }).userId,
      });
    }),
} satisfies FileRouter;
