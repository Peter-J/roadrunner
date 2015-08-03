/*
 * GillespieIntegrator.cpp
 *
 *  Created on: Apr 23, 2014
 *      Author: andy
 */

#include "GillespieIntegrator.h"
#include "rrUtils.h"
#include "rrLogger.h"
#include "rrConfig.h"

#include <cstring>
#include <assert.h>
#include <iostream>
#include <exception>
#include <ctime>
#include <limits>
#include <sstream>

using namespace std;

// min and max macros on windows interfer with max method of engine.
#undef max
#undef min

namespace rr
{
	static unsigned long defaultSeed()
	{
		int64_t seed = Config::getValue(Config::RANDOM_SEED).convert<int>();
		if (seed < 0)
		{
			// system time in mirsoseconds since 1970
			seed = getMicroSeconds();
		}

		unsigned long maxl = std::numeric_limits<unsigned long>::max() - 2;

		seed = seed % maxl;

		return (unsigned long)seed;
	}

	void GillespieIntegrator::initializeFromModel() {
//         Log(Logger::LOG_DEBUG) << "GillespieIntegrator::initializeFromModel\n";
        nReactions = model->getNumReactions();
        Log(Logger::LOG_DEBUG) << "GillespieIntegrator::initializeFromModel, nReactions = " << nReactions << "\n";
        reactionRates = new double[nReactions];
        reactionRatesBuffer = new double[nReactions];
        stateVectorSize = model->getStateVector(0);
        stateVector = new double[stateVectorSize];
        stateVectorRate = new double[stateVectorSize];

        floatingSpeciesStart = stateVectorSize - model->getNumIndFloatingSpecies();

        assert(floatingSpeciesStart >= 0);

        // get rows and columns
        model->getStoichiometryMatrix(&stoichRows, &stoichCols, 0);
        stoichData = new double[stoichRows * stoichCols];

        // fill stoichData
        model->getStoichiometryMatrix(&stoichRows, &stoichCols, &stoichData);

        setEngineSeed(getValue("seed").convert<unsigned long>());
	}

	GillespieIntegrator::GillespieIntegrator(ExecutableModel* m) :
			model(m),
			timeScale(1.0),
			stoichScale(1.0),
			stoichRows(0),
			stoichCols(0),
			stoichData(NULL),
			reactionRates(NULL),
			reactionRatesBuffer(NULL),
			stateVector(NULL),
			stateVectorRate(NULL)
	{
		// Set default integrator settings.
		addSetting("seed", defaultSeed(), "Set the seed into the random engine. (ulong)", "(ulong) Set the seed into the random engine.");
		addSetting("variable_step_size", false, "Perform a variable time step simulation. (bool)", "(bool) Enabling this setting will allow the integrator to adapt the size of each time step. This will result in a non-uniform time column.");
		addSetting("initial_time_step", 0.0, "Specifies the initial time step size. (double)", "(double) Specifies the initial time step size.");
		addSetting("minimum_time_step", 0.0, "Specifies the minimum absolute value of step size allowed. (double)", "(double) The minimum absolute value of step size allowed.");
		addSetting("maximum_time_step", 0.0, "Specifies the maximum absolute value of step size allowed. (double)", "(double) The maximum absolute value of step size allowed.");

        if (model)
            initializeFromModel();
	}

	GillespieIntegrator::~GillespieIntegrator()
	{
		delete[] reactionRates;
		delete[] reactionRatesBuffer;
		delete[] stateVector;
		delete[] stateVectorRate;
		delete[] stoichData;
        reactionRates = NULL;
        reactionRatesBuffer = NULL;
        stateVector = NULL;
        stateVectorRate = NULL;
        stoichData = NULL;
	}

    void GillespieIntegrator::syncWithModel(ExecutableModel* m)
    {
        resetSettings();
        std::cerr << "GillespieIntegrator::syncWithModel\n";
        delete[] reactionRates;
        delete[] reactionRatesBuffer;
        delete[] stateVector;
        delete[] stateVectorRate;
        delete[] stoichData;
        reactionRates = NULL;
        reactionRatesBuffer = NULL;
        stateVector = NULL;
        stateVectorRate = NULL;
        stoichData = NULL;

        model = m;
        model->reset();

        nReactions = 0;
        stateVectorSize = 0;

        timeScale = 1.;
        stoichScale = 1.;

        stoichRows = 0;
        stoichCols = 0;
        stoichData = NULL;

        initializeFromModel();
    }

    std::string GillespieIntegrator::getIntegratorName() const {
        return GillespieIntegrator::getName();
    }

    std::string GillespieIntegrator::getName() {
        return "gillespie";
    }

    std::string GillespieIntegrator::getIntegratorDescription() const {
        return GillespieIntegrator::getDescription();
    }

    std::string GillespieIntegrator::getDescription() {
        return "RoadRunner's implementation of the standard Gillespie Direct "
            "Method SSA. The granularity of this simulator is individual "
            "molecules and kinetic processes are stochastic. "
            "Results will, in general, be different in each run, but "
            "a sufficiently large ensemble of runs should be statistically correct.";
    }

    std::string GillespieIntegrator::getIntegratorHint() const {
        return GillespieIntegrator::getHint();
    }

    std::string GillespieIntegrator::getHint() {
        return "Gillespie Direct Method SSA";
    }

	Integrator::IntegrationMethod GillespieIntegrator::getIntegrationMethod() const
	{
		return Integrator::IntegrationMethod::Deterministic;
	}

	void GillespieIntegrator::setValue(string key, const Variant& val)
	{
		Integrator::setValue(key, val);

		/*	In addition to typically value-setting behavior, some settings require further changes
		within CVODE. */
		if (key == "seed")
		{
			try
			{
				unsigned long seed = val.convert<unsigned long>();
				setEngineSeed(seed);
			}
			catch (std::exception& e)
			{
				std::stringstream ss;
				ss << "Could not convert the value \"" << val.toString();
				ss << "\" to an unsigned long integer. " << endl;
				ss << "The seed must be a number between 0 and ";
				ss << std::numeric_limits<unsigned long>::max();
				ss << "; error message: " << e.what() << ".";
				throw std::invalid_argument(ss.str());
			}
		}
	}

    void GillespieIntegrator::resetSettings()
    {
        settings.clear();
        hints.clear();
        descriptions.clear();

        // Set default integrator settings.
        addSetting("seed", defaultSeed(), "Set the seed into the random engine. (ulong)", "(ulong) Set the seed into the random engine.");
        addSetting("variable_step_size", false, "Perform a variable time step simulation. (bool)", "(bool) Enabling this setting will allow the integrator to adapt the size of each time step. This will result in a non-uniform time column.");
        addSetting("initial_time_step", 0.0, "Specifies the initial time step size. (double)", "(double) Specifies the initial time step size.");
        addSetting("minimum_time_step", 0.0, "Specifies the minimum absolute value of step size allowed. (double)", "(double) The minimum absolute value of step size allowed.");
        addSetting("maximum_time_step", 0.0, "Specifies the maximum absolute value of step size allowed. (double)", "(double) The maximum absolute value of step size allowed.");
    }

	double GillespieIntegrator::integrate(double t, double hstep)
	{
		double tf = 0;
		bool singleStep;

		assert(hstep > 0 && "hstep must be > 0");

		if (getValue("variable_step_size").convert<bool>())
		{
			if (getValue("minimum_time_step").convert<double>() > 0.0)
			{
				tf = t + getValue("minimum_time_step").convert<double>();
				singleStep = false;
			}
			else
			{
				tf = t + hstep;
				singleStep = true;
			}
		}
		else
		{
			tf = t + hstep;
			singleStep = false;
		}

		Log(Logger::LOG_DEBUG) << "ssa(" << t << ", " << tf << ")";

		// get the initial state vector
		model->setTime(t);
		model->getStateVector(stateVector);

		while (t < tf)
		{
			// random uniform numbers
			double r1 = urand();
			double r2 = urand();

			assert(r1 > 0 && r1 <= 1 && r2 >= 0 && r2 <= 1);

			// sum of propensities
			double s = 0;

			// next time
			double tau = 0;

			// get the 'propensity' -- reaction rates
			model->getReactionRates(nReactions, 0, reactionRates);

			// sum the propensity
			for (int k = 0; k < nReactions; k++)
			{
				Log(Logger::LOG_DEBUG) << "reac rate: " << k << ": "
					<< reactionRates[k] <<  ", nReactions = " << nReactions;

                    {
                        int l = model->getStateVector(NULL);
                        double* svec = new double[l];
                        model->getStateVector(svec);
                        for (int z =0; z<l; ++z) {
                            Log(Logger::LOG_DEBUG) << "svec: " << svec[z];
                        }
                        delete[] svec;
                    }

				// if reaction rate is negative, that means reaction goes in reverse,
				// this is fine, we just have to reverse the stoichiometry,
				// but still need to sum the absolute value of the propensities
				// to get tau.
				s += std::abs(reactionRates[k]);
			}

			// sample tau
			if (s > 0)
			{
				tau = -log(r1) / s;
			}
			else
			{
				// no reaction occurs
				return std::numeric_limits<double>::infinity();
			}

			t = t + tau;

			// select reaction
			int reaction = -1;
			double sp = 0.0;

			r2 = r2 * s;
			for (int i = 0; i < nReactions; ++i)
			{
				sp += std::abs(reactionRates[i]);
				if (r2 < sp)
				{
					reaction = i;
					break;
				}
			}

			assert(reaction >= 0 && reaction < nReactions);

			// update chemical species
			// if rate is negative, means reaction goes in reverse, so
			// multiply by sign
			double sign = (reactionRates[reaction] > 0)
				- (reactionRates[reaction] < 0);


			for (int i = floatingSpeciesStart; i < stateVectorSize; ++i)
			{
				stateVector[i] = stateVector[i]
					+ getStoich(i - floatingSpeciesStart, reaction)
					* stoichScale * sign;

				if (stateVector[i] < 0.0) {
					Log(Logger::LOG_WARNING) << "Error, negative value of "
						<< stateVector[i]
						<< " encountred for floating species "
						<< model->getFloatingSpeciesId(i - floatingSpeciesStart);
					t = std::numeric_limits<double>::infinity();
				}
			}

			// rates could be time dependent
			model->setTime(t);
			model->setStateVector(stateVector);

			if (singleStep)
			{
				return t;
			}
		}

		return t;
	}

    void GillespieIntegrator::testRootsAtInitialTime()
    {
        vector<unsigned char> initialEventStatus(model->getEventTriggers(0, 0, 0), false);
        model->getEventTriggers(initialEventStatus.size(), 0, initialEventStatus.size() == 0 ? NULL : &initialEventStatus[0]);
        applyEvents(0, initialEventStatus);
    }

    void GillespieIntegrator::applyEvents(double timeEnd, vector<unsigned char> &previousEventStatus)
    {
        model->applyEvents(timeEnd, previousEventStatus.size() == 0 ? NULL : &previousEventStatus[0], stateVector, stateVector);

        if (timeEnd > 0.0) {
            model->setTime(timeEnd);

            // copy state vector into cvode memory
            if (stateVector)
            {
                model->getStateVector(stateVector);
            }

            // set tolerances and so forth.
//             reInit(timeEnd);
        }
    }

	void GillespieIntegrator::restart(double t0)
	{
        if (!model) {
            return;
        }

        if (t0 <= 0.0) {
            if (stateVector)
            {
                model->getStateVector(stateVector);
            }

            testRootsAtInitialTime();
        }

        model->setTime(t0);

        // copy state vector into memory
        if (stateVector)
        {
            model->getStateVector(stateVector);
        }
	}

	void GillespieIntegrator::setListener(IntegratorListenerPtr)
	{
	}

	IntegratorListenerPtr GillespieIntegrator::getListener()
	{
		return IntegratorListenerPtr();
	}

	double GillespieIntegrator::urand()
	{
		return (double)engine() / (double)engine.max();
	}

	void GillespieIntegrator::setEngineSeed(unsigned long seed)
	{
		Log(Logger::LOG_INFORMATION) << "Using user specified seed value: " << seed;

		// MSVC needs an explicit cast, fail to compile otherwise.
		engine.seed((unsigned long)seed);
	}

	} /* namespace rr */


