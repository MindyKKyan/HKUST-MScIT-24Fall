#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <stdint.h>
#include <time.h>
using namespace std;

void login2(char * input1, char * input2) {
    struct {
        char username[30];
        char good_username[30];
        int canary;
        char good_password[30];
        char password[30];
        int goodcanary;
    } __attribute__((__aligned__(1), packed)) v;

    v.canary = 34887761;
    v.goodcanary = 34887761;

    //read correct username and password
    FILE * fp = fopen("password.txt", "r");
    fgets(v.good_username, 30, fp);
    fgets(v.good_password, 30, fp);
    fclose(fp);
    v.good_username[strlen(v.good_username)-1] = '\0';
    v.good_password[strlen(v.good_password)-1] = '\0';

    strcpy(v.username, input1);
    strcpy(v.password, input2);

    //terminate strings properly for strcmp
    v.username[29] = '\0';
    v.password[29] = '\0';
    v.good_username[29] = '\0';
    v.good_password[29] = '\0';

    // check canary and login success
    if (v.canary != v.goodcanary) {
        printf("Stack overflow detected, exiting.\n\r");
        exit(-1);
    }

    if (strcmp(v.username, v.good_username) == 0 &&
      strcmp(v.password, v.good_password) == 0)
        printf("Login successful!\n");
    else
        printf("Try again.");
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        return -1;
    }

    if(access("password.txt", F_OK) == -1) {
        printf("password.txt not found; please download it and put it in this directory.\n\r");
        return -1;
    }

    if (strlen(argv[1]) < 2) {
        // invalid input
        return -1;
    }

    login2(argv[1], argv[2]);
    return 0;
}
