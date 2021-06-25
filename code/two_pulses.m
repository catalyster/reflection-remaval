function kernel=two_pulses(x0, y0, c)
% kernel that models ghost effect
  kernel=zeros(2*abs(y0)+1, 2*abs(x0)+1);
  kernel(abs(y0)+1, abs(x0)+1)=1.0;
  kernel(abs(y0)+1+y0, abs(x0)+1+x0)=c;
