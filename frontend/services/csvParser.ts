
import { PredictionData, ExtractedFeatures } from '../types.ts';

export const parsePredictionCSV = (csv: string): PredictionData | null => {
  try {
    const lines = csv.trim().split('\n');
    if (lines.length < 2) return null;
    const headers = lines[0].split(',');
    const values = lines[1].split(',');
    
    const obj: any = {};
    headers.forEach((h, i) => {
      const val = values[i];
      const numericVal = parseFloat(val);
      obj[h.trim()] = isNaN(numericVal) ? val.trim() : numericVal;
    });
    
    return obj as PredictionData;
  } catch (error) {
    console.error('Failed to parse prediction CSV', error);
    return null;
  }
};

export const parseFeaturesCSV = (csv: string): ExtractedFeatures | null => {
  try {
    const lines = csv.trim().split('\n');
    if (lines.length < 2) return null;
    const headers = lines[0].split(',');
    const values = lines[1].split(',');
    
    const obj: any = {};
    headers.forEach((h, i) => {
      const val = values[i];
      const numericVal = parseFloat(val);
      obj[h.trim()] = isNaN(numericVal) ? val.trim() : numericVal;
    });
    
    return obj as ExtractedFeatures;
  } catch (error) {
    console.error('Failed to parse features CSV', error);
    return null;
  }
};

export const downloadCSV = (content: string, filename: string) => {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
