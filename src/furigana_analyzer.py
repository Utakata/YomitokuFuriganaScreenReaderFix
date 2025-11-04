import re
from typing import List, Dict, Tuple, Optional
import numpy as np


class FuriganaAnalyzer:
    def __init__(self):
        self.furigana_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]+')
        self.kanji_pattern = re.compile(r'[\u4E00-\u9FFF]+')
        
    def detect_ruby_structure(self, text_blocks: List[Dict]) -> List[Dict]:
        ruby_pairs = []
        processed_indices = set()
        
        for i, block in enumerate(text_blocks):
            if self._is_furigana_candidate(block):
                base_text_block = self._find_base_text(block, text_blocks, i)
                if base_text_block:
                    base_index = text_blocks.index(base_text_block)
                    processed_indices.add(base_index)
                    ruby_pairs.append({
                        'base': base_text_block,
                        'ruby': block,
                        'type': 'ruby',
                        'base_index': base_index
                    })
                else:
                    ruby_pairs.append({
                        'base': block,
                        'ruby': None,
                        'type': 'text',
                        'base_index': i
                    })
            else:
                if i not in processed_indices:
                    ruby_pairs.append({
                        'base': block,
                        'ruby': None,
                        'type': 'text',
                        'base_index': i
                    })
        
        return ruby_pairs
    
    def _is_furigana_candidate(self, block: Dict) -> bool:
        text = block.get('text', '')
        size = block.get('font_size', 12)
        
        if not text:
            return False
        
        has_kana_only = bool(self.furigana_pattern.fullmatch(text.strip()))
        
        is_small = size < 8
        
        return has_kana_only and is_small
    
    def _find_base_text(self, furigana_block: Dict, all_blocks: List[Dict], furigana_index: int) -> Optional[Dict]:
        fx, fy = furigana_block.get('x', 0), furigana_block.get('y', 0)
        fw, fh = furigana_block.get('width', 0), furigana_block.get('height', 0)
        
        is_vertical = furigana_block.get('vertical', False)
        
        candidates = []
        for i, block in enumerate(all_blocks):
            if i == furigana_index:
                continue
            
            if self._is_furigana_candidate(block):
                continue
            
            bx, by = block.get('x', 0), block.get('y', 0)
            bw, bh = block.get('width', 0), block.get('height', 0)
            
            if is_vertical:
                horizontal_distance = abs(bx - fx)
                vertical_overlap = self._calculate_overlap(fy, fh, by, bh)
                if horizontal_distance < 50 and vertical_overlap > 0.5:
                    candidates.append((horizontal_distance, block))
            else:
                vertical_distance = abs(by - fy)
                horizontal_overlap = self._calculate_overlap(fx, fw, bx, bw)
                if vertical_distance < 20 and horizontal_overlap > 0.5:
                    candidates.append((vertical_distance, block))
        
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        
        return None
    
    def _calculate_overlap(self, start1: float, length1: float, start2: float, length2: float) -> float:
        end1 = start1 + length1
        end2 = start2 + length2
        
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        overlap = max(0, overlap_end - overlap_start)
        
        shorter_length = min(length1, length2)
        if shorter_length == 0:
            return 0
        
        return overlap / shorter_length
    
    def create_accessible_text_structure(self, ruby_pairs: List[Dict]) -> List[Dict]:
        accessible_structure = []
        
        for pair in ruby_pairs:
            if pair['type'] == 'ruby' and pair['ruby']:
                base_block = pair['base'].copy()
                ruby_block = pair['ruby'].copy()
                
                accessible_structure.append({
                    'text': base_block.get('text', ''),
                    'reading': ruby_block.get('text', ''),
                    'x': base_block.get('x', 0),
                    'y': base_block.get('y', 0),
                    'width': base_block.get('width', 0),
                    'height': base_block.get('height', 0),
                    'font_size': base_block.get('font_size', 12),
                    'has_furigana': True,
                    'vertical': base_block.get('vertical', False)
                })
            else:
                base_block = pair['base'].copy()
                accessible_structure.append({
                    'text': base_block.get('text', ''),
                    'reading': None,
                    'x': base_block.get('x', 0),
                    'y': base_block.get('y', 0),
                    'width': base_block.get('width', 0),
                    'height': base_block.get('height', 0),
                    'font_size': base_block.get('font_size', 12),
                    'has_furigana': False,
                    'vertical': base_block.get('vertical', False)
                })
        
        return accessible_structure
