/**
 * Simple HEIC handling utilities
 */

/**
 * Checks if file is HEIC/HEIF format
 */
export async function isHeicFile(file: File): Promise<boolean> {
  // Check extension first (fastest method)
  const ext = file.name?.split('.').pop()?.toLowerCase();
  if (ext === 'heic' || ext === 'heif') return true;

  // Fallback: Check signature (magic bytes)
  try {
    const header = await readFileHeader(file, 12);
    const headerStr = arrayBufferToString(header);
    // HEIC signatures
    return ['ftypheic', 'ftypheix', 'ftyphevc', 'ftypheim', 'ftypheis'].some((sig) =>
      headerStr.includes(sig)
    );
  } catch (err) {
    console.error('Error checking HEIC signature:', err);
    return false;
  }
}

/**
 * Converts HEIC to JPEG with compression if needed
 */
export async function convertHeicToJpeg(file: File, maxSizeMB = 4.5): Promise<File> {
  try {
    // @ts-ignore - Dynamic import
    const { heicTo } = await import('heic-to');

    // Start with high quality
    let quality = 0.9;
    let jpegFile: File;

    // Try converting with progressively lower quality until size limit is met
    do {
      // Convert with current quality
      const jpegBlob = await heicTo({
        blob: file,
        type: 'image/jpeg',
        quality: quality
      });

      // Create file with new name
      const fileName = file.name.replace(/\.(heic|heif)$/i, '.jpg');
      jpegFile = new File([jpegBlob], fileName, { type: 'image/jpeg' });

      // Reduce quality if file is still too large
      if (jpegFile.size > maxSizeMB * 1024 * 1024) {
        quality = Math.max(0.3, quality - 0.1);
      } else {
        break;
      }
    } while (quality >= 0.3);

    return jpegFile;
  } catch (error) {
    console.error('HEIC conversion error:', error);
    throw new Error('Failed to convert HEIC image');
  }
}

// Helper: Read file header
function readFileHeader(file: File, byteCount: number): Promise<ArrayBuffer> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (reader.result instanceof ArrayBuffer) {
        resolve(reader.result);
      } else {
        reject(new Error('Invalid file data'));
      }
    };
    reader.onerror = () => reject(new Error('Read error'));
    reader.readAsArrayBuffer(file.slice(0, byteCount));
  });
}

// Helper: Convert buffer to string
function arrayBufferToString(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((byte) => String.fromCharCode(byte))
    .join('');
}
