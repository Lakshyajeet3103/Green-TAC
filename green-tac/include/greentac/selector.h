#pragma once
#include "greentac/carbon.h"
#include "greentac/features.h"
#include "greentac/optimizer.h"
#include <map>
#include <string>
#include <vector>

namespace greentac {
struct Model {
    // Per-strategy linear model: metric = intercept + sum(coeff_i * feature_i)
    std::map<Strategy, std::map<std::string,double>> compileEnergy;
    std::map<Strategy, std::map<std::string,double>> runtimeEnergy;
    std::map<Strategy, std::map<std::string,double>> runtimeMs;
    bool hasCompileEnergy{false};
    bool hasRuntimeEnergy{false};
    bool hasRuntimeMs{false};
    bool fullyCalibrated{false};
};
Model loadModel(const std::string& path);

struct SelectionConfig {
    CarbonScenario carbon;
    double maxRuntimeOverBaseline{0.10};
};
struct CandidatePrediction {
    Strategy strategy;
    double compileEnergyJ{0};
    double runtimeEnergyJ{0};
    double runtimeMs{0};
    double carbonGrams{0};
    bool allowed{true};
};
struct SelectionResult { Strategy selected; std::vector<CandidatePrediction> candidates; };
SelectionResult selectStrategy(const TACProgram& baseline, const Features& features, const Model& model, const SelectionConfig& cfg);
}
