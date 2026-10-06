#include "greentac/carbon.h"
namespace greentac {
CarbonEstimate estimateCarbon(double compileEnergyJ,double runtimeEnergyJ,double runtimeMs,const CarbonScenario& s){
    const double J_PER_KWH=3.6e6; double totalGrams=(compileEnergyJ*s.compileCI_g_per_kWh + s.expectedExecutions*runtimeEnergyJ*s.runtimeCI_g_per_kWh)/J_PER_KWH; return {compileEnergyJ,runtimeEnergyJ,runtimeMs,totalGrams};
}
}
