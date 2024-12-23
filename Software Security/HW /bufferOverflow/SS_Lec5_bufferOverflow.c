//compile using:
// gcc -o bufferOverflow bufferOverflow.c -no-pie -zexecstack
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
        
void Secret(){
/*you will never see it, unless you hack the code! haha :)*/
        
        char secret[65];

        FILE *f = fopen("secret.txt", "r");
        if (f == NULL) {
                printf("secret.txt file is missing\n");
                exit(0);
        }
        fgets(secret, 65, f);
        printf("This is the secret :\n\n%s", secret);
}
                
void noSecret(){
        char answer[10];
        printf("Do you like this course (yes/no)? \n");
        gets(answer);

        printf("Great! Give us a decent evaluation score! \n\n");
}


int main(){

	noSecret();
	return 0;
}
