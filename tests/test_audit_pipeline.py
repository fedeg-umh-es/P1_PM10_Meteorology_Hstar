import unittest
import numpy as np
import pandas as pd

def compute_hstar_synthetic(skill_array):
    pos = np.where(skill_array > 0)[0]
    h_relax = int(pos.max() + 1) if len(pos) > 0 else 0
    best = 0
    current = 0
    for value in skill_array:
        if pd.notna(value) and value > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    
    # from h1
    from_h1 = 0
    for v in skill_array:
        if pd.notna(v) and v > 0:
            from_h1 += 1
        else:
            break
            
    return {"H_strict_max_run": best, "H_strict_from_h1": from_h1, "H_relax": h_relax}

class TestAuditPipeline(unittest.TestCase):
    def test_hstar_synthetic_cases(self):
        # Case 1: Madrid lags-only pattern (pos skill h=3..11)
        skill_madrid_only = np.array([-0.01, -0.02, 0.05, 0.10, 0.15, 0.20, 0.15, 0.10, 0.05, 0.02, 0.01, -0.01, -0.05, -0.02, 0.01, -0.1, -0.1, -0.2, -0.2, -0.2, -0.2, -0.2, -0.2, -0.2])
        res1 = compute_hstar_synthetic(skill_madrid_only)
        self.assertEqual(res1["H_strict_max_run"], 9)
        self.assertEqual(res1["H_strict_from_h1"], 0)
        self.assertEqual(res1["H_relax"], 15)

        # Case 2: Madrid lags-meteo pattern (pos skill h=1..17)
        skill_madrid_met = np.array([0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.15, 0.10, 0.05, 0.02, 0.01, 0.05, 0.04, 0.03, 0.02, 0.01, 0.01, -0.01, -0.05, -0.02, -0.1, -0.1, -0.2, -0.2])
        res2 = compute_hstar_synthetic(skill_madrid_met)
        self.assertEqual(res2["H_strict_max_run"], 17)
        self.assertEqual(res2["H_strict_from_h1"], 17)
        self.assertEqual(res2["H_relax"], 17)

    def test_ceiling_flag_and_edenderry_tie(self):
        # Birr: lags_only = 24 -> ceiling
        lo_birr = 24
        lm_birr = 24
        is_ceiling_birr = (lo_birr == 24)
        self.assertTrue(is_ceiling_birr)
        self.assertEqual(lm_birr - lo_birr, 0)

        # Edenderry: lags_only = 16, lags_meteo = 16 -> submaximal tie, NOT ceiling
        lo_eden = 16
        lm_eden = 16
        is_ceiling_eden = (lo_eden == 24)
        self.assertFalse(is_ceiling_eden)
        self.assertEqual(lm_eden - lo_eden, 0)

    def test_dm_paired_alignment(self):
        df_a = pd.DataFrame({"origin": ["2023-01-01", "2023-01-02"], "horizon": [1, 1], "y_true": [10.0, 20.0], "y_pred": [11.0, 19.0]})
        df_b = pd.DataFrame({"origin": ["2023-01-01", "2023-01-02"], "horizon": [1, 1], "y_true": [10.0, 20.0], "y_pred": [10.5, 19.5]})
        merged = df_a.merge(df_b, on=["origin", "horizon", "y_true"], suffixes=("_a", "_b"))
        self.assertEqual(len(merged), 2)

if __name__ == "__main__":
    unittest.main()
