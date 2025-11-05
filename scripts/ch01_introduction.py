"""
Chapter 1 — Introduction (Python mirror of R ch1_introduction.R)
Demonstrates simple arithmetic and printing, matching the R-console style.
"""
import math

def main():
    a = 3
    b = 4
    hyp = math.sqrt(a**2 + b**2)

    print("a")
    print(a)
    print("b")
    print(b)
    print("sqrt(a^2 + b^2)")
    print(hyp)  # 5.0

if __name__ == "__main__":
    main()
