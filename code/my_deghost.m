function [time, background, reflection] = my_deghost(image_path, configs, scale, gray)
format shortg
begin = fix(clock);%ɾ��С�����֣��ض�Ϊ����

%pre-process
fprintf('Pre-process...\n');

% Dependency on Patch-GMM prior
addpath('epllcode');                  

% Dependency on bounded-LBFGS Optimization package
addpath('lbfgsb/lbfgsb3.0_mex1.2');

% mycode
[pathstr,name,ext] = fileparts(image_path);%����ָ���ļ���·�����ơ��ļ�������չ��
if size(pathstr) == 0
    out_t = strcat(name, '_t',ext);
    out_r = strcat(name, '_r',ext);
else
    out_t = strcat(pathstr, '/', name, '_t',ext);%T�洢·��
    out_r = strcat(pathstr, '/', name, '_r',ext);%R�洢·��
end

I_in = im2double(imread(image_path));
d3 = size(I_in, 3);%��ѯI_in�ĵ�3��ά�ȵĳ��ȡ�
if gray == 1 && d3 > 1
    I_in = rgb2gray(I_in);
end
if scale <= 0 || scale > 1
    fprintf('Unavailable scale');
    return;
end
I_in = imresize(I_in, scale);
configs.dx = round(configs.dx * scale);%��������
configs.dy = round(configs.dy * scale);
% d3 = size(I_in, 3);
% if d3 > 1
%     fprintf('Estimating ghosting kernel...\n');
%     %[configs.dx, configs.dy, configs.c] = kernel_est(I_in, threshold);
%     %load('prova00.mat')
%     %configs.dx = dx
%     %configs.dy = dy
%     %configs.c = c
%     fprintf('Est done!\n');
%     configs.padding = configs.dx + 10;
%     if configs.dx == 0 && configs.dy == 0
%         configs.c = 1;
%     end
%     fprintf('dx = %d | dy = %d | c = %f\n', configs.dx, configs.dy, configs.c);
% else
%     configs.dx = 15;
%     configs.dy = 7;
%     configs.c = 0.5;
%     configs.padding = 0;
%     configs.match_input = 0;
%     configs.linear = 0;
% end
% end

configs.padding = max(abs(configs.dx), abs(configs.dy)) + 10;
[h, w, ~] = size(I_in);
configs.h = h;
configs.w = w;
configs.num_px = h*w;
fprintf('Pre-process done!\n');
psize = 8;
chanels = {'first', 'second', 'third'};
for i = 1 : size(I_in,3) 
  fprintf('Optimize %s chanel...\n', chanels{i});
  configs.ch=i;

  % Applying our optimization to each channel independently. 
  [I_t_k, I_r_k ] = patch_gmm(I_in(:,:,i), configs, psize);
    
  fprintf('Post-process %s chanel...\n', chanels{i});
  % Post-processings to enhance the results.
  I_t(:,:,i) = I_t_k - valid_min(I_t_k, configs.padding);%��ȥ��Сֵ��ʹͼ�����
  I_r(:,:,i) = I_r_k - valid_min(I_r_k, configs.padding);
  I_t(:,:,i) = match(I_t(:,:,i), I_in(:,:,i));
end

% Write out the results.
fprintf('Write out the results...\n');

subplot(1,3,1), imshow(I_in), title('image','FontSize', 20);
subplot(1,3,2), imshow(I_r), title('reflection','FontSize', 20);
subplot(1,3,3), imshow(I_t), title('transmission','FontSize', 20);

imwrite(I_t, out_t);
imwrite(I_r, out_r);
background = I_t;
reflection = I_r;
fprintf('All done!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n');
time = etime(fix(clock), begin);
fprintf('Total time: %d seconds\n', time);
pause;


function [I_t, I_r ] = patch_gmm(I_in, configs, psize)
% Setup for patch-based reconstruction 
h = configs.h;
w = configs.w;
c = configs.c;
dx = configs.dx;
dy = configs.dy;
lambda = 1e6; 

% Identity matrix
Id_mat = speye(h*w, h*w); %����h*w��h*wϡ�赥λ����

% Ghosting kernel K
k_mat = get_k(h, w, dx, dy, c); 

% Operator that maps an image to its ghosted version
%��ͼ��ӳ�䵽����Ӱ�汾�Ĳ�����
A = [Id_mat k_mat]; 

% patch size for patch-GMM
% psize = 16;

num_patches = (h-psize+1)*(w-psize+1);

mask=merge_two_patches(ones(psize^2, num_patches),...
            ones(psize^2, num_patches), h, w, psize);

% Use non-negative constraint
configs.non_negative = true;

% Parameters for half-quadratic regularization method
configs.beta_factor = 2;
configs.beta_i = 200;
configs.dims = [h w];

% Setup for GMM prior
load GSModel_8x8_200_2M_noDC_zeromean.mat
excludeList=[];
%noiseSD=25/255;

% Initialization, may takes a while. 
fprintf('Init...\n');
% IRLS: Iteratively reweighted least squares optimization method
[I_t_i, I_r_i ] = grad_irls(I_in, configs);
% faster option, but results are not as good.
% [I_t_i I_r_i ] = grad_lasso(I_in, configs);


% Apply patch gmm with the initial result.
% Create patches from the two layers.
est_t = im2patches(I_t_i, psize);
est_r = im2patches(I_r_i, psize);

niter = 25;
beta  = configs.beta_i;

fprintf('Optimizing...\n');
for i = 1 : niter
  fprintf('Optimizine iter %d of %d...\n', i, niter);
  % Merge the patches with bounded least squares
  f_handle = @(x)(lambda * A'*(A*x) + beta*(mask.*x));
  sum_piT_zi = merge_two_patches(est_t, est_r, h, w, psize);
  sum_zi_2 = norm(est_t(:))^2 + norm(est_r(:))^2;
  z = lambda * A'*I_in(:) + beta * sum_piT_zi; 

  % Non-neg. optimization by L-BFGSB
  opts    = struct( 'factr', 1e4, 'pgtol', 1e-8, 'm', 50);
  opts.printEvery     = 50;
  l = zeros(numel(z),1);
  u = ones(numel(z),1);

  fcn = @(x)( lambda * norm(A*x - I_in(:))^2 + ...
      beta*( sum(x.*mask.*x - 2 * x.* sum_piT_zi(:)) + sum_zi_2));
  grad = @(x)(2*(f_handle(x) - z));
  fun     = @(x)fminunc_wrapper( x, fcn, grad); 
  [out, ~, info] = lbfgsb(fun, l, u, opts );

  out = reshape(out, h, w, 2);
  I_t = out(:,:,1); 
  I_r = out(:,:,2); 

  % ʹ������ָ���Ƭ
  est_t = im2patches(I_t, psize);
  est_r = im2patches(I_r, psize);
  noiseSD=(1/beta)^0.5;
  [est_t, t_cost]= aprxMAPGMM(est_t,psize,noiseSD,[h w], GS,excludeList);
  [est_r, r_cost]= aprxMAPGMM(est_r,psize,noiseSD,[h w], GS,excludeList);

  beta = beta*configs.beta_factor;

end

function out = merge_two_patches(est_t, est_r, h, w, psize)
  % �ϲ���Ƭ
  t_merge = merge_patches(est_t, h, w, psize);
  r_merge = merge_patches(est_r, h, w, psize);
  out = cat(1, t_merge(:), r_merge(:));%��ֱ��������������

function out = match(i,ex)
  % ��ԭʼͼ���ȫ����Ϣ�봫��ͼ���ȫ����Ϣ����ƥ��
  sig = sqrt(sum((ex-mean(ex(:))).^2)/sum((i-mean(i(:))).^2));
  out = sig*(i-mean(i(:))) + mean(ex(:)); 


