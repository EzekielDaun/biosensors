a = intmax('uint16');
fprintf('Initial uint16 value %5d is %016s in binary\n',a,dec2bin(a))
for i = 1:16
  a = bitshift(a,1);
  fprintf('Shifted uint16 value %5d is %016s in binary\n',a,dec2bin(a))
end