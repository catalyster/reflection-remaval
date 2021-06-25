function [] = deghosts(path)
    try
      diary('log_else_rgb.txt');
      scale = 1;

      load('C:\\Users\\catalyst\\Desktop\\graduationDesign\\code\test\\synthetic.mat');
      %fprintf('Starting deghost synthetic (20 images)...\n');
      %ii = [1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20];
      %for i=1:1
          %fprintf('Starting deghost prova_%s...\n', int2str(ii(i)));
          %[time, T, R] = my_deghost(synthetic(ii(i)).name, synthetic(ii(i)).configs, scale, 0);
      %end

      [~, name, ~] = fileparts(path);
      str = split(name, "_");
      fprintf('Starting deghost prova_%s...\n', char(str(2)));
      [time, T, R] = my_deghost(path, synthetic(str2num(char(str(2)))).configs, scale, 0);

      fprintf('Done!!!!!!!!!!!!!!!!!');
      diary off
      %system('shutdown -s');
  catch
      fprintf('Error\n');
      diary off
      %system('shutdown -s');
  end
end