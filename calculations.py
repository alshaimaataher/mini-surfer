import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
from pylab import *

class Calculations():
    def __init__(self,table,radius,width,length):
        self.table=table
        self.radius=radius
        self.width=width
        self.length=length
        self.distance=np.max([width,length])
        self.X_ax,self.Y_ax,self.Z_tot=self.cal_z_total()
        
    def cal_overlap(self):
        return (2-(self.distance/self.radius))*100
    
    def cal_z_total(self):
        X=[]
        Y=[]
        Z=[]
        for row in range(0,self.table.rowCount()):
            if(self.table.item(row,0) and self.table.item(row,1) and self.table.item(row,2)):
                if((self.table.item(row,0).text()).isnumeric() and (self.table.item(row,1)).text().isnumeric() and (self.table.item(row,2).text()).isnumeric()):
                    x = self.table.item(row, 0).text() 
                    y = self.table.item(row, 1).text() 
                    z = self.table.item(row, 2).text() 
            
                    X.append(int(x))
                    Y.append(int(y))
                    Z.append(float(z))
            
            
        num_sprnk=4
        max_x=np.max(X) # horizontal axies
        max_y=np.max(Y) # vertical axies
        if(max_y==max_x):
            self.z_index=max_y
        else:
            raise Exception('error the number of X elements and Y elements is not equal')
        
        x_extend=self.width
        y_extend=self.length
        self.abs_diff=np.zeros([self.z_index,self.z_index])
        step=1
        Z_2D=np.reshape(Z,(max_y+1,max_x+1),'F')
        arr1=np.zeros([max_y+1,x_extend-(max_x+1)])
        arr2=np.zeros([y_extend-(max_y+1),x_extend])
        Z_2D=np.append(Z_2D,arr1,1)
        Z_2D=np.append(Z_2D,arr2,0)
        [X_ax,Y_ax] = np.meshgrid(np.arange(0,x_extend,step),np.arange(0,y_extend,step))
        spr_arr={} 
        spr_arr[0,0] =X_ax
        spr_arr[0,1] =Y_ax
        spr_arr[0,2] = Z_2D
        
        spr_arr[1,0] =np.flip(X_ax,1)
        spr_arr[1,1] =Y_ax
        spr_arr[1,2] = np.flip(Z_2D,1)
        
        spr_arr[2,0] =np.flip(X_ax,1)
        spr_arr[2,1] =np.flip(Y_ax,0)
        spr_arr[2,2] = np.flip(np.flip(Z_2D,0),1)
        
        spr_arr[3,0]=X_ax
        spr_arr[3,1] =np.flip(Y_ax,0)
        spr_arr[3,2] = np.flip(Z_2D,0)
        Z_tot=np.zeros([x_extend,y_extend])
        for x_dim in range(0,x_extend):
            for y_dim in range(0,y_extend):
                for sprnkl_index in range (0,num_sprnk):
                   Z_tot[x_dim,y_dim]=Z_tot[x_dim,y_dim]+spr_arr[sprnkl_index,2][y_dim,x_dim]
#        Z_tot=Z_tot.transpose()

        return X_ax,Y_ax,Z_tot

    def cal_cu(self):
        Z_bar=np.mean(np.mean(self.Z_tot[:,:]))
        for count in range(0,self.z_index):
            self.abs_diff[0,count]=abs(self.Z_tot[self.z_index-1,self.z_index-1]-Z_bar)
        sum_diff=np.sum(self.abs_diff)

        CU=(1-(sum_diff/(self.z_index*Z_bar)))
        return CU*100

    def cal_du(self):
        Z_bar=np.mean(np.mean(self.Z_tot[:,:]))
        K=int(np.ceil(self.z_index/4))
        sorted_Z=np.sort(self.Z_tot[:,:])
        multiple_min=sorted_Z[0,0:K]
        Z_lq=np.mean(multiple_min)
        DU_lq=Z_lq/Z_bar
        return DU_lq*100
    
    def plot(self,ax,canvas):
        ax.plot_surface(self.X_ax,self.Y_ax,self.Z_tot.transpose(),cmap=plt.cm.plasma)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('net water volum')
        ax.set_title('Pressure')
        plt.show()
        canvas.draw()