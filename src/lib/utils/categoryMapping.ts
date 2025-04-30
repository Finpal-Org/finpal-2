/**
 * Category mapping for standardized receipt categories, Based on Azure Document Intelligence 4.0 receipt categories
 */
export const categoryMapping: Record<string, string> = {
  Meal: 'Meal',
  Supplies: 'Supplies',
  Hotel: 'Hotel',
  'Fuel&Energy': 'Fuel',
  Transportation: 'Travel',
  'Transportation.CarRental': 'Car',
  Communication: 'Communication',
  Subscriptions: 'Subscriptions',
  Entertainment: 'Entertainment',
  Training: 'Training',
  Healthcare: 'Health',
  Other: 'Other'
};

/**
 * List of standardized categories to use in dropdowns
 */
export const standardCategories = [
  'Meal',
  'Supplies',
  'Hotel',
  'Fuel',
  'Travel',
  'Car',
  'Communication',
  'Subscriptions',
  'Entertainment',
  'Training',
  'Health',
  'Other'
];

export function standardizeCategory(rawCategory: string): string {
  if (!rawCategory) return 'Other';

  // Check if the category exists in our mapping
  if (rawCategory in categoryMapping) {
    return categoryMapping[rawCategory];
  }

  return rawCategory;
}
