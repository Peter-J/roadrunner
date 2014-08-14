#ifndef rrGPUSimIntegratorH
#define rrGPUSimIntegratorH

#include "Integrator.h"
#include "rrRoadRunnerOptions.h"
#include "Configurable.h"

#include <string>
#include <vector>

/**
 * CVode vector struct
 */
typedef struct _generic_N_Vector *N_Vector;

namespace rr
{

using std::string;

class ExecutableModel;
class RoadRunner;

namespace rrgpu
{

/**
 * @internal
 * The integrator implemented by CVODE.
 */
class GPUSimIntegrator : public Integrator
{
public:
    GPUSimIntegrator(ExecutableModel* oModel, const SimulateOptions* options);

    virtual ~GPUSimIntegrator();

    /**
     * creates a new xml element that represent the current state of this
     * Configurable object and all if its child objects.
     */
    virtual _xmlNode *createConfigNode();

    /**
     * Given an xml element, the Configurable object should pick its needed
     * values that are stored in the element and use them to set its
     * internal configuration state.
     */
    virtual void loadConfig(const _xmlDoc* doc);

    virtual double integrate(double t0, double tf);

    /**
     * copies the state vector out of the model and into the integrator vector,
     * re-initializes the integrator.
     */
    virtual void restart(double timeStart);

    /**
     * set the options the integrator will use.
     */
    virtual void setSimulateOptions(const SimulateOptions* options);

    /**
     * the integrator can hold a single listener. If clients require multicast,
     * they can create a multi-cast listener.
     */
    virtual void setListener(IntegratorListenerPtr);

    /**
     * get the integrator listener
     */
    virtual IntegratorListenerPtr getListener();

    /**
     * implement dictionary interface
     */
    virtual void setValue(const std::string& key, const rr::Variant& value);

    virtual Variant getValue(const std::string& key) const;

    virtual bool hasKey(const std::string& key) const;

    virtual int deleteValue(const std::string& key);

    virtual std::vector<std::string> getKeys() const;

    /**
     * get a description of this object, compatable with python __str__
     */
    virtual std::string toString() const;

    /**
     * get a short descriptions of this object, compatable with python __repr__.
     */
    virtual std::string toRepr() const;

    /**
     * get the name of this integrator
     */
    virtual std::string getName() const;

private:
};

} // namespace rrgpu

} // namespace rr

#endif