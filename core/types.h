#ifndef TYPES_H
#define TYPES_H

struct IntentContext {
  double control, attack, defense, tempo, risk;
  IntentContext(double c = 1, double a = 1, double d = 1, double t = 1,
                double r = 1)
      : control(c), attack(a), defense(d), tempo(t), risk(r) {}
};

#endif
