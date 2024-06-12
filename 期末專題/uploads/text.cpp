#include<iostream>
#include<vector>
#include<cstdlib>
#include<ctime> 
using namespace std;

int gcd(int a,int b){
	if(!b)return a;
	return gcd(b,a%b);
}

int fib(int x){
	if(x==1 or x==2)return 1;
	return fib(x-1)+fib(x-2);
}

double max_min(vector<double> *x,int l){
	vector<double>& y=*x;
	double max=0,min=999999;
	for(int i=0;i<l;i++){
		if(y[i]>max)max=y[i];
		if(y[i]<min)min=y[i];
	}
	cout << "max=" << max <<endl;
	cout << "min=" << min << endl;
	return 0;
}
int main(){
	srand(time(0));
	int b[6];
	for(int i=0;i<6;i++){
		int a=rand()%49+1;
		for(int j=0;j<i;j++){
			if(a==b[j]){
				i--;
				break;
			}
		b[i]=a;
		}
	}
	for(int i=0;i<6;i++){
		cout << b[i] << " ";
	}
	//double v[10]={-127, 480, 18, 1005, 1827, 5288, -635, 145, 307};
	//vector <double> vec(v,v+10);
	//max_min(&vec,vec.size());
}
