
export interface PredictionData {
  Timestamp: string;
  Predicted_MMSE: number;
  Max_MMSE: number;
  Percentage: number;
  Cognitive_Status: string;
  Risk_Level: string;
  Risk_Category: string;
  Confidence_Percent: number;
  Step_Time_MS: number;
  Stride_Time_MS: number;
  IDS_MS: number;
  TDS_MS: number;
  SLS_MS: number;
  Stance_MS: number;
  Swing_MS: number;
}

export interface ExtractedFeatures {
  Step_Time_MS: number;
  Stride_Time_MS: number;
  IDS_MS: number;
  TDS_MS: number;
  SLS_MS: number;
  Stance_MS: number;
  Swing_MS: number;
  Step_Time_Sec: number;
  Stride_Time_Sec: number;
  Initial_Double_Support_Sec: number;
  Terminal_Double_Support_Sec: number;
  Single_Limb_Support_Sec: number;
  Stance_Time_Sec: number;
  Swing_Time_Sec: number;
  Timestamp: string;
  Duration_Seconds: number;
  Total_Samples: number;
  Left_Heel_Strikes: number;
  Left_Toe_Offs: number;
  Right_Heel_Strikes: number;
  Right_Toe_Offs: number;
  Predicted_MMSE: number;
  Cognitive_Status: string;
  Risk_Level: string;
  Confidence_Percent: number;
}

export enum RiskLevel {
  GREEN = 'green',
  YELLOW = 'yellow',
  ORANGE = 'orange',
  RED = 'red'
}
