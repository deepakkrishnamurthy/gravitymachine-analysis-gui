# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 11:50:01 2018

@author: Francois
"""

% A model for cercariae based on a four-link swimmer with torsional spring
% %                             5|(4)
% %       (1)      (2)      (3)  | 
% %   1 --------o--------o-------|4
%              2         3       |
%                               6|
% Link 2 is the body frame link
%**************************************************************************   
function []=T_swimmer_four_link_gravity(varargin)
clear all
close all
folder=['/Users/deepak/Google Drive/Swimming_parasites/Theory_Simulations/Simulation_data'];
%folder=['D:\Google Drive\Swimming_parasites\Theory_Simulations\Simulation_data'];

k1_array=logspace(-1/2,2,25);     %array of values for torsional spring stiffness of head-tail joint
k2_array=logspace(-1/2,2,25);     %array of values for torsional spring stiffness of fork-tail joint   
len_k1=length(k1_array);
len_k2=length(k2_array);
%--------------------------------------------------------------------------
% Parameters
%--------------------------------------------------------------------------
% l1d=0.78;           % Dimensions from image processing 
% l2d=0.6;
% l3d=0.6;
% l4d=1;

l1d=0.78;           % Dimensions from image processing 
l2d=0.6;
l3d=0.6;
l4d=1;

lc=(l1d+l2d+l3d)/2;
l1=l1d/lc;       % Non-dimensional link lengths
l2=l2d/lc;       % Non-dimensional link lengths    
l3=l3d/lc;       % Non-dimensional link lengths
l4=l4d/lc;      % Non-dimensional link lengths

half_swimmer_length=(l1+l2+l3)/2;
Amp=(290/2)*pi/180;   % Amplitude of actuation of the active link (kinematic control)
Amp=0
Time=20;
t_stroke=5;
dt=0.05;
torque_amp=2;
Omega=1/t_stroke;
slenderness_ratio=10;
Cl=2*pi/(log(slenderness_ratio));   % Drag coefficient in the tangential direction    
anis=2;             % The drag anisotropy between longitudnal and transverse motion
Cn=anis*Cl;         % Drag coefficient to transverse motion
k_hat_1=6;                          % k_hat_3=k3/(\mu \Omega l_2^3) Non-dimensional spring stiffness of HEAD in PER RADIAN (NOTE THE CONVERSION pi/180)
k_hat_3=2;                         % k_hat_3=k3/(\mu \Omega l_2^3) Non-dimensional spring stiffness of TAIL in PER RADIAN (NOTE THE CONVERSION pi/180)
f_b=0.94;                              % buoyant force (due to swimmer being heavier or lighter than the fluid)
%--------------------------------------------------------------------------
% Matrices in governing equation
%--------------------------------------------------------------------------
I_link=[1 0; 0 0; 0 1];     % Matrix encoding link and joint geometry I_link(i,j)=1 if the ith link is affected by the jth joint I_link(i,j)=0 otherwise
% R_link=@(alpha,l)Cl.*l.*[1+sin(alpha).^2 -sin(alpha).*cos(alpha) 0;-sin(alpha).*cos(alpha) 1+cos(alpha).^2 0; 0 0 l.^2./6];
R_link=@(alpha,l)Cl.*l.*[cos(alpha).^2+(Cn./Cl).*sin(alpha).^2 -sin(alpha).*cos(alpha).*(Cn./Cl-1) 0;-sin(alpha).*cos(alpha).*(Cn./Cl-1) sin(alpha).^2+(Cn./Cl).*cos(alpha).^2 0; 0 0 (Cn./Cl).*l.^2./12];

R=@(alpha1,alpha2,alpha3,l1,l2,l3,l4)blkdiag(R_link(-alpha1,l1),R_link(0,l2),R_link(alpha2,l3),R_link(alpha2+alpha3,l4)); % 12x12
% R_temp=@(alpha1,alpha2,alpha3,theta,l1,l2,l3,l4)blkdiag(R_link(-alpha1,l1),R_link(theta,l2),R_link(alpha2,l3),R_link(alpha2+alpha3,l4)); % 12x12 : Note the angles here are specified 
R_temp=@(alpha1,alpha2,alpha3,theta,l1,l2,l3,l4)blkdiag(R_link(-(alpha1-theta),l1),R_link(theta,l2),R_link(alpha2+theta,l3),R_link(alpha2+alpha3+theta,l4)); % 12x12 : Note the angles here are specified 

% Matrix connecting link velocity to body velocities
T1=@(alpha)[1 0 -l1*sin(alpha)./2; 0 1 -(l1*cos(alpha)+l2)./2;0 0 1];        % 3x3
T2=eye(3,3);                        
T3=@(alpha)[1 0 -l3*sin(alpha)/2; 0 1 l2/2+l3*cos(alpha)/2;0 0 1];          % 3x3
T4=@(alpha)[1 0 -l3*sin(alpha);0 1 l2/2+l3*cos(alpha);0 0 1];
T=@(alpha1,alpha2)[T1(alpha1);T2;T3(alpha2);T4(alpha2)];                               % 12x3
%Matrix connecting shape velocity to link velocity
E1=@(alpha)[l1.*sin(alpha)./2 0 0; l1.*cos(alpha)/2 0 0; -1 0 0];
E2=zeros(3,3);
E3=@(alpha)[0 -l3*sin(alpha)/2 0;0 l3*cos(alpha)/2 0; 0 1 0];                  % 3x3
E4=@(alpha)[0 -l3*sin(alpha) 0;0 l3*cos(alpha) 0; 0 1 1];
% E=@(alpha1,alpha2)zeros(12,3);
E=@(alpha1,alpha2)[E1(alpha1);E2;E3(alpha2);E4(alpha2)];                               % 12x3

rot_matrix=@(theta)[cos(theta) -sin(theta) 0; sin(theta) cos(theta) 0;0 0 1];
rot_matrix_2d=@(theta)[cos(theta) -sin(theta); sin(theta) cos(theta)];
R_bb=@(alpha1,alpha2,alpha3,l1,l2,l3,l4)T(alpha1,alpha2)'*R(alpha1,alpha2,alpha3,l1,l2,l3,l4)*T(alpha1,alpha2); % 3x3
R_bu=@(alpha1,alpha2,alpha3,l1,l2,l3,l4)T(alpha1,alpha2)'*R(alpha1,alpha2,alpha3,l1,l2,l3,l4)*E(alpha1,alpha2); % 3x2
R_uu=@(alpha1,alpha2,alpha3,l1,l2,l3,l4)E(alpha1,alpha2)'*R(alpha1,alpha2,alpha3,l1,l2,l3,l4)*E(alpha1,alpha2); % 2x2

R_bb_temp=@(alpha1,alpha2,alpha3,theta,l1,l2,l3,l4)T(alpha1-theta,alpha2+theta)'*R_temp(alpha1,alpha2,alpha3,theta,l1,l2,l3,l4)*T(alpha1-theta,alpha2+theta); % 3x3
A=@(alpha1,alpha2,alpha3,l1,l2,l3,l4)-inv(R_bb(alpha1,alpha2,alpha3,l1,l2,l3,l4))*R_bu(alpha1,alpha2,alpha3,l1,l2,l3,l4); % 3x2
H=@(alpha1,alpha2,alpha3,l1,l2,l3,l4)inv(R_uu(alpha1,alpha2,alpha3,l1,l2,l3,l4)-R_bu(alpha1,alpha2,alpha3,l1,l2,l3,l4)'*inv(R_bb(alpha1,alpha2,alpha3,l1,l2,l3,l4))*R_bu(alpha1,alpha2,alpha3,l1,l2,l3,l4));
G=@(alpha1,alpha2,alpha3,l1,l2,l3,l4)A(alpha1,alpha2,alpha3,l1,l2,l3,l4)*H(alpha1,alpha2,alpha3,l1,l2,l3,l4);
Hindex=@(H,ii,jj)H(ii,jj);
% det_H=@(alpha1,alpha2,l1,l2,l3)det(H(alpha1,alpha2,l1,l2,l3));


%% INITIAL CONDITIONS AND TIME INTEGRATION
% [t,X]=ode45(@ode_purcell_three_link,[0 pi],[0 0 0 Amp Amp]);
% X0=[0;0;0;0;0;pi/2];

X0=[0;0;0;0;0;0];
% [t,X]=RK4(@ode_T_swimmer,dt,0,X0,Time);
% [t,X]=RK4(@ode_T_swimmer_kinematic,dt,0,X0,Time);
% [t,X]=ode45(@ode_T_swimmer,[0 Time],X0);
options=odeset('RelTol',1e-6,'AbsTol',1e-6);
[t,X]=ode45(@ode_T_swimmer_kinematic,[0 Time],X0,options);
t(length(t))
t_len=length(t);
t=t';
X=X';
% X(1:2,:)=X(1:2,:)./half_swimmer_length;
size(t)
size(X)

%--------------------------------------------------------------------------
% POST PROCESSING
%--------------------------------------------------------------------------
xy_vel=zeros(2,length(t));
%--------------------------------------------------------------------------
% Calculating the instantaneous swimmer velocity based on the center of link 1
%--------------------------------------------------------------------------
% for ii=1:length(t)-1
%     t1=t(1,ii);
%     t2=t(1,ii+1);
%     x=X(:,ii);
%     x10=[x(1)-l2/2*cos(x(3))-(l1/2).*cos(x(4)-x(3));x(2)+(l1/2)*sin(x(4)-x(3))-(l2/2)*sin(x(3))];
%     x1=X(:,ii+1);
%     x11=[x1(1)-l2/2*cos(x1(3))-(l1/2).*cos(x1(4)-x1(3));x1(2)+(l1/2)*sin(x1(4)-x1(3))-(l2/2)*sin(x1(3))];
%     xy_vel(:,ii)=(x11-x10)./(t2-t1);
% end

avg_vel_x=(X(1,length(t))-X(1,1))/(t(length(t))-t(1))
avg_vel_y=(X(2,length(t))-X(2,1))/(t(length(t))-t(1))

% coordinates of the center of link 1 on the swimmer as labelled above (This serves as
% the head position in our model)
xh=zeros(2,length(t));
xh(1,:)=X(1,:)-(l2/2)*cos(X(3,:))-(l1/2).*cos(X(4,:)-X(3,:));
xh(2,:)=X(2,:)-(l2/2)*sin(X(3,:))+(l1/2).*sin(X(4,:)-X(3,:));

% coordinates of point-2 on the swimmer as labelled above
x2j=zeros(2,length(t));
x2j(1,:)=X(1,:)-(l2/2)*cos(X(3,:));
x2j(2,:)=X(2,:)-(l2/2)*sin(X(3,:));
% Torque at the passive joint
% TAU=k_hat*(pi/2-X(5,:));

%==========================================================================
%---------------------------------------------------------------------------
%Efficiency calculation
%---------------------------------------------------------------------------
% t vector and X vector X(1) : xposition X(2): y position X(3): theta
% (angle of the body frame) X(4): \phi1, X(5) \phi_2 and X(6) \phi_3





% Instantaneous velocity of COM
t_rep=repmat(t,[6 1]);
t_diff=diff(t,1);
V=zeros(6,t_len);

% Calculate the velocity of the body frame using central differences and
% forward and backward differences at the boundaries

for ii=1:t_len
    if(ii==1)
        V(:,ii)=(X(:,ii+1)-X(:,ii))./(t_rep(:,ii+1)-t_rep(:,ii));
    elseif (ii==t_len)
        V(:,ii)=(X(:,ii)-X(:,ii-1))./(t_rep(:,ii)-t_rep(:,ii-1));
    else
        V(:,ii)=(X(:,ii+1)-X(:,ii-1))./(t_rep(:,ii+1)-t_rep(:,ii-1));
%         V(:,ii)=(X(:,ii+1)-X(:,ii))./(t_rep(:,ii+1)-t_rep(:,ii));
    end
end

% V=diff(X,1,2)./diff(t_rep,1,2); % Instantaneous body and shape velocities
V_body=V(1:3,:);
V_shape=V(4:end,:);

% Calculate the average swimmer velocity
avg_window=round_odd(ceil(t_len/Time))          % average over last end_N points
V_avg=zeros(2,t_len);
size(smooth(V_body(1,:),avg_window))
V_avg(1,:)=smooth(V_body(1,:),avg_window)';
V_avg(2,:)=smooth(V_body(2,:),avg_window)';

V_avg_mag=dot(V_avg,V_avg,1).^(1/2);
V_hat=V_avg./repmat(V_avg_mag,[2 1]);           % 2x t_len


P_diss=zeros(1,t_len);
FdotU=zeros(1,t_len);
eta=zeros(1,t_len);

figure(3), hold on;
% subplot(1,2,1), hold on
set(gca,'FontName','Arial','FontSize',16);
plot(t(1:end),V_body(1,:),'r-','LineWidth',2);
plot(t(1:end),V_body(2,:),'g--','LineWidth',2);
plot(t(1:end),V_avg(1,:),'ro-','LineWidth',2);
plot(t(1:end),V_avg(2,:),'g^-','LineWidth',2)
xlabel('Time','FontSize',16);
ylabel('V_{avg}(t)','FontSize',16)


for ii=1:t_len
    ii
    x=X(1,ii);
    y=X(2,ii);
    theta=X(3,ii);
    phi1=X(4,ii);
    phi2=X(5,ii);
    phi3=X(6,ii);
    V_hat_temp=V_hat(:,ii);
    dot(V_hat_temp,V_hat_temp,1)
    V_temp=T(phi1-theta,phi2+theta)*V_body(:,ii)+E(phi1-theta,phi2+theta)*V_shape(:,ii);      %T: 12x3 and E : 12x3 -> V_temp: 12x1
    F_links=-R_temp(phi1,phi2,phi3,theta,l1,l2,l3,l4)*V_temp       % 12x12 12x1
    F_body=T(phi1-theta,phi2+theta)'*F_links
    P_diss(ii)=-dot(F_links,V_temp);      % 12x12 12x1 dot 12x1=1x1
    F_links_forces=F_links([1:2,4:5,7:8,10:11],1);    % 8x1
%     F_link_torques=F_links([3,6,9,10],1);
    F_links_forces=reshape(F_links_forces,[2 4])
    sum(F_links_forces,2)
    error_forces(ii)=norm(sum(F_links_forces,2),Inf)/norm(F_links_forces,Inf);
%     norm(sum(F_links_forces),2)/norm(F_links_forces,2)
%     sum(F_link_torques)
    V_hat_rep=repmat(V_hat_temp,[1 4]);
    F_dot_U=dot(F_links_forces,V_hat_rep,1);
    
    F_thrust=sum(F_dot_U(F_dot_U>=0))
    F_drag=sum(F_dot_U(F_dot_U<0))
    
    eta(ii)=F_thrust*V_avg_mag(ii)./P_diss(ii);
end



norm(error_forces,Inf)
mean(t_diff).^2
figure(6), hold on;
plot(t,error_forces,'r-');

% subplot(1,2,1), hold on
% set(gca,'FontName','Arial','FontSize',16);
% plot(t,V_avg(1,:),'ro-','LineWidth',2);
% plot(t,V_avg(2,:),'g^-','LineWidth',2)
% xlabel('Time','FontSize',16);
% ylabel('V_{avg}(t)','FontSize',16)

% subplot(1,2,2), hold on
% set(gca,'FontName','Arial','FontSize',16);
% plot(t,eta,'ro-','LineWidth',2);
% xlabel('Time','FontSize',16);
% ylabel('\eta(t)','FontSize',16);
% box on;  
%==========================================================================
%--------------------------------------------------------------------------
% MOVIES
%--------------------------------------------------------------------------
Frames=moviein(length(t));
for ii=1:length(t)-1
    x=X(:,ii);
    x1=[x(1)-l2/2*cos(x(3))-l1.*cos(x(4)-x(3));x(2)+l1*sin(x(4)-x(3))-(l2/2)*sin(x(3))];
    x2=[x(1)-cos(x(3))*l2/2;x(2)-(l2/2)*sin(x(3))];
    x3=[x(1)+cos(x(3))*l2/2;x(2)+(l2/2)*sin(x(3))];
    x4=[x3(1)+l3*cos(x(5)+x(3));x3(2)+l3*sin(x(5)+x(3))];
    x5=[x4(1)+l4*cos(x(6)+x(5)+x(3))/2;x4(2)+l4*sin(x(5)+x(6)+x(3))/2];
    x6=[x4(1)-l4*cos(x(6)+x(5)+x(3))/2;x4(2)-l4*sin(x(5)+x(6)+x(3))/2];
    link1=draw_line(x1,x2);
    link2=draw_line(x2,x3);
    link3=draw_line(x3,x4);
    link4=draw_line(x5,x6);

    h=figure(13); hold on;
%     set(gcf,'Position',[100 100 1100 600]);
    cla
    plot(link1(1,:),link1(2,:),'b-','LineWidth',3);
    plot(link2(1,:),link2(2,:),'g-','LineWidth',3);
    plot(link3(1,:),link3(2,:),'r-','LineWidth',3);
    plot(link4(1,:),link4(2,:),'k-','LineWidth',3);
%     plot(x_rot(1,1),x_rot(2,1),'ro');
%     plot((x2(1)+x3(1))/2,(x2(2)+x3(2))/2,'ro','LineWidth',2);
%     plot(x(1),x(2),'ko','LineWidth',2);
    plot(xh(1,ii),xh(2,ii),'ro')
    xlabel('x','FontSize',24);
    ylabel('y','FontSize',24);
    axis equal
    axis([-2 2 -2 2]);
    grid on
    box on
    pause(0.01)
    set(gca,'FontSize',16);
%     Frames(:,ii)=getframe(h);
%     set(h, 'Color', 'w');
%      file1=['D:\Swimming_parasites\Theory_Simulations\simulation_images\four_link_swimmer','\',int2str(ii),'.tif'];
%      saveas(h,file1)...