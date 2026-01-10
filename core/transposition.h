#ifndef TRANSPOSITION_H
#define TRANSPOSITION_H
#include <mutex>
#include <unordered_map>


struct TTEntry {
  int score;
  int depth;
};

class TranspositionTable {
  std::unordered_map<uint64_t, TTEntry> table;
  std::mutex mtx;

public:
  void store(uint64_t key, int score, int depth) {
    std::lock_guard<std::mutex> lock(mtx);
    table[key] = {score, depth};
  }
  bool probe(uint64_t key, TTEntry &out) {
    std::lock_guard<std::mutex> lock(mtx);
    auto it = table.find(key);
    if (it == table.end())
      return false;
    out = it->second;
    return true;
  }
  void clear() {
    std::lock_guard<std::mutex> lock(mtx);
    table.clear();
  }
};
#endif
