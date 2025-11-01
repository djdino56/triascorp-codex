export interface BacktestConfig {
  instrumentName: string;
  interval: string;
  start?: string | null;
  end?: string | null;
  initialCash: number;
  maxOpenPositions: number;
  takeProfit: number;
  stopLoss: number;
  shortWindow: number;
  longWindow: number;
}

export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Position {
  entryPrice: number;
  entryTime: string;
  size: number;
  exitPrice?: number;
  exitTime?: string;
  stopLoss?: number;
  takeProfit?: number;
}

export interface TradeResult {
  position: Position;
  profit: number;
}

export interface BacktestReport {
  trades: TradeResult[];
  finalCash: number;
  wins: number;
  losses: number;
}

export interface BacktestRequestBody {
  config: BacktestConfig;
  candles?: Candle[];
}

export interface BacktestResponseBody {
  report: BacktestReport;
}
