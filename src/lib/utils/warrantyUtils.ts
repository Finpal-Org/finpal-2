/**
 * Utility functions for warranty management
 */

/**
 * Calculate warranty expiry date based on receipt date or creation date
 * @param startDate Receipt date string or null
 * @param createdTime Firestore timestamp or date when receipt was added
 * @param periodDays Warranty period in days
 * @returns Expiry date as a string in DD/MM/YYYY format
 */
export function calculateWarrantyExpiry(
  startDate: string | null | undefined,
  createdTime: Date | null | undefined,
  periodDays: number
): string {
  // Use receipt date if available, otherwise use creation date or current date
  let baseDate: Date;

  if (startDate) {
    baseDate = new Date(startDate);
    // Check if the date is valid
    if (isNaN(baseDate.getTime())) {
      baseDate = createdTime ? new Date(createdTime) : new Date();
    }
  } else {
    baseDate = createdTime ? new Date(createdTime) : new Date();
  }

  // Add warranty period days to the base date
  const expiryDate = new Date(baseDate);
  expiryDate.setDate(expiryDate.getDate() + periodDays);

  // Format to DD/MM/YYYY
  const monthStr = (expiryDate.getMonth() + 1).toString().padStart(2, '0');
  const dayStr = expiryDate.getDate().toString().padStart(2, '0');
  const yearStr = expiryDate.getFullYear();

  return `${dayStr}/${monthStr}/${yearStr}`;
}

/**
 * Get the last day of a specific month in a specific year
 * @param year Year
 * @param month Month (0-11)
 * @returns The last day of the month
 */
function getLastDayOfMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate();
}

/**
 * Check if a warranty has expired
 * @param expiryDate Warranty expiry date string in any valid format
 * @returns Boolean indicating if warranty has expired
 */
export function isWarrantyExpired(expiryDate: string): boolean {
  // Parse the date in DD/MM/YYYY format
  const parts = expiryDate.split('/');
  let expiry: Date;

  if (parts.length === 3) {
    // Handle DD/MM/YYYY format
    expiry = new Date(
      parseInt(parts[2]), // Year
      parseInt(parts[1]) - 1, // Month (0-indexed)
      parseInt(parts[0]) // Day
    );
  } else {
    // Try standard date parsing
    expiry = new Date(expiryDate);
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0); // Reset hours to compare dates only

  // Check if the date is valid
  if (isNaN(expiry.getTime())) {
    return true; // If date is invalid, consider warranty expired
  }

  return today > expiry;
}

/**
 * Calculate days remaining until warranty expiry
 * @param expiryDate Warranty expiry date string in any valid format
 * @returns Number of days remaining (negative if expired)
 */
export function getWarrantyDaysRemaining(expiryDate: string): number {
  // Parse the date in DD/MM/YYYY format
  const parts = expiryDate.split('/');
  let expiry: Date;

  if (parts.length === 3) {
    // Handle DD/MM/YYYY format
    expiry = new Date(
      parseInt(parts[2]), // Year
      parseInt(parts[1]) - 1, // Month (0-indexed)
      parseInt(parts[0]) // Day
    );
  } else {
    // Try standard date parsing
    expiry = new Date(expiryDate);
  }

  const today = new Date();

  // Set both dates to midnight to ensure we count full days
  expiry.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);

  // Check if the date is valid
  if (isNaN(expiry.getTime())) {
    return -1; // If date is invalid, consider warranty expired
  }

  // Calculate difference in milliseconds and convert to days
  const differenceMs = expiry.getTime() - today.getTime();
  return Math.ceil(differenceMs / (1000 * 60 * 60 * 24));
}

/**
 * Convert warranty period from months to days
 * @param months Number of months
 * @returns Approximate number of days
 */
export function monthsToDays(months: number): number {
  // Average days per month (365.25 / 12)
  return Math.round(months * 30.44);
}

/**
 * Format a date string to DD/MM/YYYY
 * @param dateStr Date string in any valid format
 * @returns Formatted date string or null if invalid
 */
export function formatDate(dateStr: string | undefined): string | null {
  if (!dateStr) return null;

  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return null;

    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const year = date.getFullYear();

    return `${day}/${month}/${year}`;
  } catch (error) {
    return null;
  }
}
