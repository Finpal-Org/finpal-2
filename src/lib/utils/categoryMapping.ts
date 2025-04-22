/**
 * Category mapping for standardized receipt categories, Based on Azure Document Intelligence 4.0 receipt categories
 */
export const categoryMapping: Record<string, string> = {
  Meal: 'Meal',
  Supplies: 'Supplies',
  Hotel: 'Hotel',
  'Fuel&Energy': 'Fuel',
  Transportation: 'Travel',
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
export const standardCategories = Object.values(categoryMapping);

export function standardizeCategory(rawCategory: string): string {
  if (!rawCategory) return 'Other';

  // Check if the category exists in our mapping
  if (rawCategory in categoryMapping) {
    return categoryMapping[rawCategory];
  }

  return rawCategory;
}
