function [] = fftPlot(t,Y)
% Subtract the DC compnent
Y = Y - mean(Y);
L = length(Y);

fY = fft(Y);
P2 = abs(fY/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

SamplingFreq = 1/mean(t(2:end)-t(1:end-1));
f = SamplingFreq*(0:(L/2))/L;

figure, hold on;
subplot(121), hold on;
plot(t,Y,'r-','LineWidth',1);
title('Signal in time domain')
xlabel('t (seconds)')
ylabel('Y(t)')
subplot(122), hold on;
plot(f,P1,'g--','LineWidth',1)
title('Single-Sided Amplitude Spectrum of Y(t)')
xlabel('f (Hz)')
ylabel('|P1(f)|')

end
