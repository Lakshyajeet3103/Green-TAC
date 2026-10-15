#pragma once
namespace greentac {
struct CarbonScenario { double compileCI_g_per_kWh{400}; double runtimeCI_g_per_kWh{400}; double expectedExecutions{1}; };
struct CarbonEstimate { double compileEnergyJ; double runtimeEnergyJ; double runtimeMs; double totalCarbonGrams; };
CarbonEstimate estimateCarbon(double compileEnergyJ, double runtimeEnergyJ, double runtimeMs, const CarbonScenario& s);
}
