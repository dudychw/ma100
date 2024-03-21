//@version=5
indicator("MACD with LONG and SHORT Labels", overlay=true)

// параметры MACD
fast_length = input.int(12, "Fast Length")
slow_length = input.int(26, "Slow Length")
signal_length = input.int(9, "Signal Smoothing")

// расчет MACD
fast_ma = ta.ema(close, fast_length)
slow_ma = ta.ema(close, slow_length)
macd = fast_ma - slow_ma
signal = ta.ema(macd, signal_length)

// вывод на график
plot(macd, color=color.blue, title="MACD")
plot(signal, color=color.red, title="Signal")

// точки входа
long_entry = macd > signal and macd[1] <= signal[1]
short_entry = macd < signal and macd[1] >= signal[1]

// отображение точек на графике
plotshape(long_entry ? macd : na, style=shape.circle, location=location.belowbar, color=color.new(color.green, 0), size=size.small)
plotshape(short_entry ? macd : na, style=shape.circle, location=location.abovebar, color=color.new(color.red, 0), size=size.small)

// добавление меток LONG и SHORT при пересечении сигнальной линии и границы нуля
zero_cross_long = ta.crossover(signal, 0)
if zero_cross_long
    label.new(bar_index, low, "LONG", xloc.bar_index, yloc.belowbar, color=color.new(color.green, 0), style=label.style_label_up, textcolor=color.white, size=size.small)

zero_cross_short = ta.crossunder(signal, 0)
if zero_cross_short
    label.new(bar_index, high, "SHORT", xloc.bar_index, yloc.abovebar, color=color.new(color.red, 0), style=label.style_label_down, textcolor=color.white, size=size.small)