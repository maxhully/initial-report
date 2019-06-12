import numpy as np
import pandas


def splitting_energy(assignment1, assignment2, population, energy_function=np.log):
    df = pandas.DataFrame(
        {
            "assignment1": assignment1,
            "assignment2": assignment2,
            "population": population,
        }
    )
    return (
        df.groupby(["assignment1", "assignment2"])["population"]
        .sum()
        .apply(energy_function)
        .sum()
    )
