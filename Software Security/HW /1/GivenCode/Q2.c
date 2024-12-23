/* compiled using:
   gcc -fno-stack-protector -no-pie -ggdb -Q2.c -o Q2

*/
#include <string.h>
#include <stdio.h>

/* global variables in the data segment*/
/* normal buffer overflow happens on the stack */
/* can't touch the global variables */
int state1 = 0; 
int state2 = 0;

        
void fun1(){

   state1 = 1;
   printf("You solved first 1/3 of this harder question!\n");
}

void fun2(){

   if (state1 == 1){

      state2 = 1;
      printf("You solved first 2/3 of this harder question!\n");

   }

}

void fun3(){

    if (state1==1 && state2==1){

       printf("You have solved completely this harder question!!\n");

    } 
}



void noSecret(){
   char answer[10];
   printf("Do you like this question (yes/no)? \n");
   gets(answer);

}


int main(){
   noSecret();
   if (state1==0 || state2==0){
      printf("Unfortunately, you haven't solved this question!\n");
   }

   return 0;
}
