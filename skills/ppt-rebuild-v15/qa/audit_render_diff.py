from __future__ import annotations
from pathlib import Path
import cv2
import numpy as np

def compare_images(reference_path: str, rendered_path: str, threshold: int = 20):
    ref = cv2.imread(reference_path)
    ren = cv2.imread(rendered_path)
    if ref is None or ren is None:
        return {'status':'error', 'message':'image not found'}
    ren = cv2.resize(ren, (ref.shape[1], ref.shape[0]))
    diff = cv2.absdiff(ref, ren)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    mae = float(np.mean(gray))
    changed = float(np.mean(gray > threshold))
    return {'status':'pass' if changed < 0.22 else 'review', 'mae': mae, 'changed_ratio_gt20': changed}
