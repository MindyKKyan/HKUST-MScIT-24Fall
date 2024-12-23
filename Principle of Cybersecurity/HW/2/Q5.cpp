#include <string>
#include <iostream>

float fuzzTest(std::string s) {
    int n = 0;
    for (int i = 0; i < s.size(); ++i) {
        if (s[i] >= 'A' && s[i] <= 'z') {
            ++n;
        }
    }
    return n / s.size();
}

int main() {
    std::string s;
    std::getline(std::cin, s);
    std::cout << fuzzTest(s) << std::endl;
    return 0;
}