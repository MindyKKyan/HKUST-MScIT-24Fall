/*compiled using:
 gcc -O0 -ggdb Q1.c -o Q1  
*/

#include <stdio.h>
#include <string.h>

void funct2(){
 
    printf("You solve this easy question!\n");

}

void funct1(){ 
   char input[2];
   int decision=0;

   gets(input);

   if (decision==0x2){
      funct2();
   }
   else{ 
      printf("I am sorry, you haven't solved the question...\n");
  }

}


void main(){

   funct1();
}
