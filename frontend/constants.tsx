
export const GAIT_NORMAL_RANGES = [
  { parameter: 'Step Time', min: 450, max: 650, unit: 'ms', description: 'Duration of one step' },
  { parameter: 'Stride Time', min: 950, max: 1250, unit: 'ms', description: 'Duration of one full gait cycle' },
  { parameter: 'Stance Time', min: 600, max: 800, unit: 'ms', description: 'Total foot contact phase' },
  { parameter: 'Swing Time', min: 350, max: 500, unit: 'ms', description: 'Foot non-contact phase' },
  { parameter: 'Single Limb Support', min: 350, max: 450, unit: 'ms', description: 'One foot contact' },
  { parameter: 'Initial Double Support', min: 100, max: 200, unit: 'ms', description: 'Loading response' },
  { parameter: 'Terminal Double Support', min: 100, max: 200, unit: 'ms', description: 'Pre-swing phase' }
];


export const FALLBACK_PREDICTION_CSV = `Timestamp,Predicted_MMSE,Max_MMSE,Percentage,Cognitive_Status,Risk_Level,Risk_Category,Confidence_Percent,Step_Time_MS,Stride_Time_MS,IDS_MS,TDS_MS,SLS_MS,Stance_MS,Swing_MS
2026-01-01 11:11:36,27,30,90.0,Normal Cognition,green,Low Risk,65.9,550.0,1035.0,152.0,151.0,389.0,701.5,389.0`;

export const FALLBACK_FEATURES_CSV = `Step_Time_MS,Stride_Time_MS,IDS_MS,TDS_MS,SLS_MS,Stance_MS,Swing_MS,Step_Time_Sec,Stride_Time_Sec,Initial_Double_Support_Sec,Terminal_Double_Support_Sec,Single_Limb_Support_Sec,Stance_Time_Sec,Swing_Time_Sec,Timestamp,Duration_Seconds,Total_Samples,Left_Heel_Strikes,Left_Toe_Offs,Right_Heel_Strikes,Right_Toe_Offs,Predicted_MMSE,Cognitive_Status,Risk_Level,Confidence_Percent
550,1035,152,151,389,701,389,0.55,1.035,0.152,0.151,0.389,0.701,0.389,2026-01-01 11:11:36,12.5,1250,12,12,11,11,27,Normal Cognition,green,65.9`;


export const PREDICTION_CSV_PATH = '/results/prediction_results.csv';
export const FEATURES_CSV_PATH = '/results/extracted_features.csv';

export async function loadPredictionCSV(): Promise<string> {
  try {
    const res = await fetch(PREDICTION_CSV_PATH);
    if (!res.ok) throw new Error(`Failed to fetch ${PREDICTION_CSV_PATH}`);
    const text = await res.text();
    if (text && text.trim().length > 0) return text;
    throw new Error('Empty prediction CSV');
  } catch (err) {
    console.warn('Using fallback prediction CSV due to:', err);
    return FALLBACK_PREDICTION_CSV;
  }
}

export async function loadFeaturesCSV(): Promise<string> {
  try {
    const res = await fetch(FEATURES_CSV_PATH);
    if (!res.ok) throw new Error(`Failed to fetch ${FEATURES_CSV_PATH}`);
    const text = await res.text();
    if (text && text.trim().length > 0) return text;
    throw new Error('Empty features CSV');
  } catch (err) {
    console.warn('Using fallback features CSV due to:', err);
    return FALLBACK_FEATURES_CSV;
  }
}
