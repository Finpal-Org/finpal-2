import type { ReceiptData } from '../../types';
import { saveAs } from 'file-saver';
import * as ExcelJS from 'exceljs';

/**
 * Exports receipt data to Excel format (XLSX)
 * @param receipts Array of receipt data to export
 * @param fileName Optional custom filename (defaults to 'receipts-export.xlsx')
 */
export async function exportReceiptsToExcel(
  receipts: ReceiptData[],
  fileName: string = 'receipts-export.xlsx'
): Promise<void> {
  // Create a new workbook
  const workbook = new ExcelJS.Workbook();

  // Add a worksheet
  const worksheet = workbook.addWorksheet('Receipts');

  // Define columns
  worksheet.columns = [
    { header: 'Receipt ID', key: 'id', width: 15 },
    { header: 'Merchant', key: 'merchantName', width: 25 },
    { header: 'Category', key: 'category', width: 15 },
    { header: 'Date', key: 'date', width: 12 },
    { header: 'Total', key: 'total', width: 10 },
    { header: 'Subtotal', key: 'subtotal', width: 10 },
    { header: 'Tax', key: 'totalTax', width: 10 },
    { header: 'Address', key: 'address', width: 30 },
    { header: 'Phone', key: 'phone', width: 15 },
    { header: 'Tip', key: 'tip', width: 10 }
  ];

  // Add header row
  const headerRow = worksheet.getRow(1);
  headerRow.font = { bold: true };

  // Add style to headers
  worksheet.getRow(1).eachCell((cell) => {
    cell.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFE0E0E0' }
    };
    cell.border = {
      top: { style: 'thin' },
      left: { style: 'thin' },
      bottom: { style: 'thin' },
      right: { style: 'thin' }
    };
  });

  // Add data rows
  receipts.forEach((receipt) => {
    // Add row with data mapped to columns
    worksheet.addRow({
      id: receipt.id || '',
      merchantName: receipt.merchantName || 'Unknown',
      category: receipt.category || 'Other',
      date: receipt.date || '',
      total: receipt.total || '',
      subtotal: receipt.subtotal || '',
      totalTax: receipt.totalTax || '',
      address: receipt.address || '',
      phone: receipt.phone || '',
      tip: receipt.tip || '0'
    });
  });

  // Auto-fit columns (optional improvement)
  worksheet.columns.forEach((column) => {
    const lengths = column.values?.filter((v) => v).map((v: any) => v.toString().length);
    if (lengths && lengths.length > 0) {
      const maxLength = Math.max(...lengths);
      column.width = maxLength < 10 ? 10 : maxLength > 50 ? 50 : maxLength;
    }
  });

  // Apply borders to all data cells
  for (let i = 2; i <= receipts.length + 1; i++) {
    worksheet.getRow(i).eachCell({ includeEmpty: true }, function (cell) {
      cell.border = {
        top: { style: 'thin' },
        left: { style: 'thin' },
        bottom: { style: 'thin' },
        right: { style: 'thin' }
      };
    });
  }

  // Format number columns
  worksheet.getColumn('total').numFmt = '0.00';
  worksheet.getColumn('subtotal').numFmt = '0.00';
  worksheet.getColumn('totalTax').numFmt = '0.00';
  worksheet.getColumn('tip').numFmt = '0.00';

  // Generate a buffer
  const buffer = await workbook.xlsx.writeBuffer();

  // Save the file using file-saver
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  });
  saveAs(blob, fileName);
}

/**
 * Exports receipts grouped by category
 * @param receipts Array of receipt data to export
 * @param fileName Optional custom filename
 */
export async function exportReceiptsByCategory(
  receipts: ReceiptData[],
  fileName: string = 'receipts-by-category.xlsx'
): Promise<void> {
  // Create a new workbook
  const workbook = new ExcelJS.Workbook();

  // Group receipts by category
  const categories = {} as Record<string, ReceiptData[]>;

  receipts.forEach((receipt) => {
    const category = receipt.category || 'Other';
    if (!categories[category]) {
      categories[category] = [];
    }
    categories[category].push(receipt);
  });

  // Create a summary worksheet
  const summarySheet = workbook.addWorksheet('Summary');

  // Define summary columns
  summarySheet.columns = [
    { header: 'Category', key: 'category', width: 20 },
    { header: 'Receipt Count', key: 'count', width: 15 },
    { header: 'Total Amount', key: 'total', width: 15 }
  ];

  // Style summary header
  summarySheet.getRow(1).font = { bold: true };
  summarySheet.getRow(1).eachCell((cell) => {
    cell.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFE0E0E0' }
    };
    cell.border = {
      top: { style: 'thin' },
      left: { style: 'thin' },
      bottom: { style: 'thin' },
      right: { style: 'thin' }
    };
  });

  // Add summary data
  Object.entries(categories).forEach(([category, categoryReceipts]) => {
    // Calculate total for this category
    const categoryTotal = categoryReceipts.reduce((sum, receipt) => {
      const total = receipt.total ? parseFloat(receipt.total.toString()) : 0;
      return sum + (isNaN(total) ? 0 : total);
    }, 0);

    summarySheet.addRow({
      category,
      count: categoryReceipts.length,
      total: categoryTotal.toFixed(2)
    });

    // Create a worksheet for each category
    const worksheet = workbook.addWorksheet(category.substring(0, 31)); // Excel sheet names limited to 31 chars

    // Define columns for category worksheet (same as main export)
    worksheet.columns = [
      { header: 'Receipt ID', key: 'id', width: 15 },
      { header: 'Merchant', key: 'merchantName', width: 25 },
      { header: 'Date', key: 'date', width: 12 },
      { header: 'Total', key: 'total', width: 10 },
      { header: 'Subtotal', key: 'subtotal', width: 10 },
      { header: 'Tax', key: 'totalTax', width: 10 },
      { header: 'Address', key: 'address', width: 30 },
      { header: 'Phone', key: 'phone', width: 15 }
    ];

    // Style category header
    worksheet.getRow(1).font = { bold: true };
    worksheet.getRow(1).eachCell((cell) => {
      cell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFE0E0E0' }
      };
      cell.border = {
        top: { style: 'thin' },
        left: { style: 'thin' },
        bottom: { style: 'thin' },
        right: { style: 'thin' }
      };
    });

    // Add data rows for this category
    categoryReceipts.forEach((receipt) => {
      worksheet.addRow({
        id: receipt.id || '',
        merchantName: receipt.merchantName || 'Unknown',
        date: receipt.date || '',
        total: receipt.total || '',
        subtotal: receipt.subtotal || '',
        totalTax: receipt.totalTax || '',
        address: receipt.address || '',
        phone: receipt.phone || '',
        currency: receipt.currency || '',
        createdTime: receipt.createdTime || '',
        payment: receipt.payment || '',
        taxDescription: receipt.taxDescription || ''
      });
    });

    // Format number columns
    worksheet.getColumn('total').numFmt = '0.00';
    worksheet.getColumn('subtotal').numFmt = '0.00';
    worksheet.getColumn('totalTax').numFmt = '0.00';
  });

  // Format summary number column
  summarySheet.getColumn('total').numFmt = '0.00';

  // Generate a buffer
  const buffer = await workbook.xlsx.writeBuffer();

  // Save the file using file-saver
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  });
  saveAs(blob, fileName);
}
