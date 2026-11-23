#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

#include "heuristics/heuristic_factory.h"

using Clock = std::chrono::steady_clock;

class Output final : public MaxCutCallback, public QUBOCallback {
public:
    Output(const MaxCutInstance& graph, Clock::time_point deadline)
        : graph(graph), deadline(deadline) {}

    bool Report(const MaxCutSimpleSolution& solution, bool best, double) override {
        if (best) emit(solution);
        return Clock::now() < deadline;
    }

    bool Report(const MaxCutSimpleSolution& solution, bool best, double time, int) override {
        return Report(solution, best, time);
    }

    bool Report(const QUBOSimpleSolution& solution, bool best, double) override {
        if (best) emit(MaxCutSimpleSolution(solution, graph, nullptr));
        return Clock::now() < deadline;
    }

    bool Report(const QUBOSimpleSolution& solution, bool best, double time, int) override {
        return Report(solution, best, time);
    }

    void emit(const MaxCutSimpleSolution& solution) const {
        const auto& assignments = solution.get_assignments();
        std::string bits;
        bits.reserve(assignments.size());
        for (int value : assignments) {
            if (value != 1 && value != -1) throw std::runtime_error("Invalid spin");
            bits.push_back(value == 1 ? '1' : '0');
        }
        const double weight = solution.get_weight();
        if (!std::isfinite(weight) || std::round(weight) != weight) {
            throw std::runtime_error("Expected an integer cut weight");
        }
        std::cout << "CUT " << static_cast<long long>(weight) << ' ' << bits << std::endl;
    }

private:
    const MaxCutInstance& graph;
    Clock::time_point deadline;
};

int main(int argc, char** argv) {
    if (argc != 5) {
        std::cerr << "usage: mqlib_output METHOD GRAPH SECONDS SEED\n";
        return 2;
    }
    const auto start = Clock::now();
    const std::string method = argv[1];
    MaxCutInstance graph(argv[2]);
    const double seconds = std::stod(argv[3]);
    const int seed = std::stoi(argv[4]);
    HeuristicFactory factory;
    const int slots = method == "PORTFOLIO" ? 8 : 1;
    for (int slot = 0; slot < slots; ++slot) {
        const std::string label = slots == 1 ? method :
            (slot % 2 == 0 ? "BURER2002" : "FESTA2002GVNSPR");
        const auto duration = std::chrono::duration<double>(seconds * (slot + 1) / slots);
        const auto end = start + std::chrono::duration_cast<Clock::duration>(duration);
        const double remaining = std::chrono::duration<double>(end - Clock::now()).count();
        if (remaining <= 0) continue;
        std::srand(seed + slot);
        Output output(graph, end);
        if (factory.ValidMaxCutHeuristicCode(label)) {
            std::unique_ptr<MaxCutHeuristic> run(
                factory.RunMaxCutHeuristic(label, graph, remaining, false, &output));
            output.emit(run->get_best_solution());
        } else if (factory.ValidQUBOHeuristicCode(label)) {
            QUBOInstance qubo(graph);
            std::unique_ptr<QUBOHeuristic> run(
                factory.RunQUBOHeuristic(label, qubo, remaining, false, &output));
            output.emit(MaxCutSimpleSolution(run->get_best_solution(), graph, nullptr));
        } else {
            std::cerr << "Unknown method\n";
            return 2;
        }
    }
    return 0;
}
