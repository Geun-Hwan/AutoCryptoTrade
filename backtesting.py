import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 전략 미설정.
""" TODO 여러 전략별로 백테스팅 후 승률, 수익률 체크 """
class TradingBacktest:
    def __init__(self, data_path, initial_balance=1000, leverage=10 , postion_ratio=0.5):
        self.data = pd.read_csv(data_path)
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        
        
        
        self.data = self.data.sort_values('timestamp').reset_index(drop=True)

        self.initial_balance = initial_balance
        self.leverage = leverage
        self.balance = initial_balance
        self.position = None  # None, 'long', 'short'
        self.entry_price = None

        self.trades = []  # 거래내역 저장
        self.signals = []  # 진입 신호 저장
        self.equity_curve = []  # 시점별 자산 변화 추적
        self.position_size =0
        self.postion_ratio= postion_ratio
        # 보조 지표 초기화
        self.data['rsi'] = np.nan
        self.data['long_upper_tail'] = False
        self.data['long_lower_tail'] = False

    def calculate_rsi(self, window=14):
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window).mean()
        loss = -delta.where(delta < 0, 0).rolling(window).mean()
        rs = gain / loss
        rsi = 100 - 100 / (1 + rs)
        self.data['rsi'] = rsi.fillna(50)  # 초반값 50으로 대체

    def detect_long_tails(self):
        # 꼬리: 위 꼬리 = high - max(open, close), 아래 꼬리 = min(open, close) - low
        upper_tail = self.data['high'] - self.data[['open', 'close']].max(axis=1)
        lower_tail = self.data[['open', 'close']].min(axis=1) - self.data['low']
        candle_body = abs(self.data['close'] - self.data['open'])
        self.data['long_upper_tail'] = upper_tail > candle_body * 0.8
        self.data['long_lower_tail'] = lower_tail > candle_body * 0.8

    def run_backtest(self):
        self.calculate_rsi()
        self.detect_long_tails()
        self.data['ma5'] = self.data['close'].rolling(window=5).mean()
        self.data['ma20'] = self.data['close'].rolling(window=20).mean()
        self.data['ma_dead_cross'] = (self.data['ma5'] < self.data['ma20'])

        for i in range(len(self.data) -1):
            row = self.data.iloc[i]
            target = self.data.iloc[i+1]
            
            
            if self.balance < 10:
                unrealized = 0
                self.equity_curve.append(self.balance + unrealized)
                continue
            
           

            # 익절/손절 체크
            if self.position is not None:
                if self.position == 'long':
                    take_profit = self.entry_price * 1.007
                    stop_loss = self.entry_price * 0.97

                    if row['high'] >= take_profit:
                        profit = (take_profit - self.entry_price) * self.leverage * (self.position_size / self.entry_price)
                        self.balance += profit
                        self.trades.append({'index': i, 'type': 'exit', 'direction': 'long', 'price': take_profit, 'profit': profit})

                        print(f"[{row['timestamp']}] LONG 포지션 익절 종료: 진입가 {self.entry_price:.4f}, 종료가 {take_profit:.4f}, "
                            f"포지션 크기 ${self.position_size:.2f}, 수익 ${profit:.2f}, 잔고 ${self.balance:.2f}")

                        self.position = None
                        self.entry_price = None
                        self.position_size = 0

                    elif row['low'] <= stop_loss:
                        loss = (stop_loss - self.entry_price) * self.leverage * (self.position_size / self.entry_price)
                        self.balance += loss
                        self.trades.append({'index': i, 'type': 'exit', 'direction': 'long', 'price': stop_loss, 'profit': loss})

                        print(f"[{row['timestamp']}] LONG 포지션 손절 종료: 진입가 {self.entry_price:.4f}, 종료가 {stop_loss:.4f}, "
                            f"포지션 크기 ${self.position_size:.2f}, 손실 ${loss:.2f}, 잔고 ${self.balance:.2f}")

                        self.position = None
                        self.entry_price = None
                        self.position_size = 0

                elif self.position == 'short':
                    take_profit = self.entry_price * 0.993
                    stop_loss = self.entry_price * 1.03

                    if row['low'] <= take_profit:
                        profit = (self.entry_price - take_profit) * self.leverage * (self.position_size / self.entry_price)
                        self.balance += profit
                        self.trades.append({'index': i, 'type': 'exit', 'direction': 'short', 'price': take_profit, 'profit': profit})

                        print(f"[{row['timestamp']}] SHORT 포지션 익절 종료: 진입가 {self.entry_price:.4f}, 종료가 {take_profit:.4f}, "
                            f"포지션 크기 ${self.position_size:.2f}, 수익 ${profit:.2f}, 잔고 ${self.balance:.2f}")

                        self.position = None
                        self.entry_price = None
                        self.position_size = 0

                    elif row['high'] >= stop_loss:
                        loss = (self.entry_price - stop_loss) * self.leverage * (self.position_size / self.entry_price)
                        self.balance += loss
                        self.trades.append({'index': i, 'type': 'exit', 'direction': 'short', 'price': stop_loss, 'profit': loss})

                        print(f"[{row['timestamp']}] SHORT 포지션 손절 종료: 진입가 {self.entry_price:.4f}, 종료가 {stop_loss:.4f}, "
                            f"포지션 크기 ${self.position_size:.2f}, 손실 ${loss:.2f}, 잔고 ${self.balance:.2f}")

                        self.position = None
                        self.entry_price = None
                        self.position_size = 0
                        
                  # 포지션 없을 때 진입 시도
            if self.position is None:
                entry_amount = self.balance  * self.postion_ratio

                if row['rsi'] >= 50 and not row['long_upper_tail'] or row['long_lower_tail'] :
                    self.signals.append({'index': i, 'direction': 'long', 'type': 'signal'})
                    self.position = 'long'
                    self.entry_price = target['open']
                    self.position_size = entry_amount
                    self.trades.append({'index': i, 'type': 'entry', 'direction': 'long', 'price': target['open']})

                    print(f"[{target['timestamp']}] LONG 포지션 진입: 가격 {target['open']:.4f}, 포지션 크기 ${entry_amount:.2f}, 잔고 ${self.balance:.2f}")


                    

                elif row['long_upper_tail'] and row['rsi'] <= 30:
                    self.signals.append({'index': i, 'direction': 'short', 'type': 'signal'})
                    self.position = 'short'
                    self.entry_price = target['open']
                    self.position_size = entry_amount
                    self.trades.append({'index': i, 'type': 'entry', 'direction': 'short', 'price': target['open']})

                    print(f"[{target['timestamp']}] SHORT 포지션 진입: 가격 {target['open']:.4f}, 포지션 크기 ${entry_amount:.2f}, 잔고 ${self.balance:.2f}")
                    
                elif row['long_upper_tail'] and row['rsi'] <= 30:
                    self.signals.append({'index': i, 'direction': 'short', 'type': 'signal'})
                    self.position = 'short'
                    self.entry_price = target['open']
                    self.position_size = entry_amount
                    self.trades.append({'index': i, 'type': 'entry', 'direction': 'short', 'price': target['open']})

                    print(f"[{target['timestamp']}] SHORT 포지션 진입: 가격 {target['open']:.4f}, 포지션 크기 ${entry_amount:.2f}, 잔고 ${self.balance:.2f}")
                    
                    

           

            # 자산 가치 기록
            if self.position == 'long':
                unrealized = (row['close'] - self.entry_price) * self.leverage * (self.position_size / self.entry_price)
            elif self.position == 'short':
                unrealized = (self.entry_price - row['close']) * self.leverage * (self.position_size / self.entry_price)
            else:
                unrealized = 0
            self.equity_curve.append(self.balance + unrealized)


    def report(self):
        total_profit = sum(t['profit'] for t in self.trades if t['type']=='exit')
        final_balance = self.balance
        total_trades = len([t for t in self.trades if t['type']=='exit'])
        wins = [t for t in self.trades if t['type']=='exit' and t['profit'] > 0]
        losses = [t for t in self.trades if t['type']=='exit' and t['profit'] <= 0]
        win_rate = len(wins)/total_trades*100 if total_trades > 0 else 0
        avg_win = np.mean([t['profit'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['profit'] for t in losses]) if losses else 0

        print(f"총 수익: $ {total_profit:.2f}")
        print(f"최종 잔고: $ {final_balance:.2f}")
        print(f"총 거래 수: {total_trades}")
        print(f"승률: {win_rate:.2f} %")
        print(f"평균 수익: $ {avg_win:.2f}")
        print(f"평균 손실: $ {avg_loss:.2f}")

    def plot_results(self):
        df = self.data.copy()
        df['balance'] = pd.Series(self.equity_curve)

        fig = go.Figure()

        # 캔들스틱 차트
        fig.add_trace(go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Candles"
        ))

        # 진입 신호 (노란 별)
        if self.signals:
            sig_x = [self.data.iloc[s['index']]['timestamp'] for s in self.signals]
            sig_y = [self.data.iloc[s['index']]['close'] for s in self.signals]
            fig.add_trace(go.Scatter(
                x=sig_x, y=sig_y,
                mode='markers',
                marker=dict(symbol='star', size=14, color='yellow'),
                name='Entry Signal'
            ))

        # 거래 신호 (진입 삼각형, 청산 x)
        for trade in self.trades:
            trade_row = df.iloc[trade['index']]
            if trade['type'] == 'entry':
                color = 'darkgreen' if trade['direction'] == 'long' else 'darkred'
                symbol = 'triangle-up' if trade['direction'] == 'long' else 'triangle-down'
            else:
                color = 'blue' if trade['direction'] == 'long' else 'orange'
                symbol = 'x'

            fig.add_trace(go.Scatter(
                x=[trade_row['timestamp']],
                y=[trade_row['close']],
                mode='markers+text',
                marker=dict(color=color, size=12, symbol=symbol),
                text=[trade['type'].capitalize()],
                name=f"{trade['type'].capitalize()} {trade['direction']}",
                textposition='top center'
            ))

        # 잔고 변화선 (오른쪽 y축)
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['balance'],
            mode='lines',
            name='Equity Curve',
            line=dict(color='purple', width=2),
            yaxis='y2'
        ))

        fig.update_layout(
            title="Backtest Result with Entry/Exit & Signal Points + Equity Curve",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_white",
            xaxis_rangeslider_visible=False,
            height=700,
            xaxis=dict(
                tickmode='linear',
                dtick=max(len(df)//15, 1),
                tickangle=45
            ),
            yaxis2=dict(
                title='Balance',
                overlaying='y',
                side='right',
                showgrid=False
            )
        )

        fig.show()



# 사용 예시
if __name__ == "__main__":
    # 백테스트 실행
    bt = TradingBacktest('./data/bit_candles_20250511_to_20250610.csv' ,postion_ratio=1)
    # bt = TradingBacktest('eth_candles_20250511_to_20250610.csv' ,postion_ratio=1)
    
    bt.run_backtest()
    bt.report()
    bt.plot_results()
