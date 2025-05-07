/**
 * Generates a unique ID using a combination of timestamp and random string
 * Format: "a" + timestamp in base36 + random string in base36
 * This provides good uniqueness without requiring crypto APIs
 * @returns A unique string ID prefixed with "a"
 */
export function generateUniqueId(): string {
  const timestamp = new Date().getTime().toString(36);
  const randomStr = Math.random().toString(36).substring(2, 10);
  return `a${timestamp}${randomStr}`;
}
