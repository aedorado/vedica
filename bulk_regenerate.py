#!/usr/bin/env python3
"""
Regenerate all existing charts with planet_dignity and vimshottari_dasha.
Does NOT import new charts, only regenerates existing ones.
"""

import sys
import json
from core.database import get_conn
from core.planet_dignity import calculate_planet_dignity
from core.analytics import rebuild_cache

def regenerate_all_charts():
    """Regenerate planet_dignity and vimshottari_dasha for all existing charts."""
    conn = get_conn()
    c = conn.cursor()
    
    # Get all charts
    c.execute('SELECT id, rasi_chart, vimshottari_dasha FROM charts ORDER BY id')
    charts = c.fetchall()
    
    if not charts:
        print("❌ No charts found in database")
        return
    
    print(f"🔄 Regenerating {len(charts)} charts...\n")
    
    updated_count = 0
    error_count = 0
    
    for i, (chart_id, rasi_json, dasha_json) in enumerate(charts, 1):
        rasi_chart = json.loads(rasi_json or '[]') if rasi_json else None
        dasha = json.loads(dasha_json or '{}') if dasha_json else None
        
        try:
            # Calculate planet dignity if rasi_chart exists
            if rasi_chart:
                planet_dignity = calculate_planet_dignity(rasi_chart)
                c.execute(
                    'UPDATE charts SET planet_dignity = ? WHERE id = ?',
                    (json.dumps(planet_dignity), chart_id)
                )
                updated_count += 1
                status = "✓ Dignity"
            else:
                status = "⊘ No rasi"
            
            # Check vimshottari_dasha
            if not dasha or not dasha.get('raw'):
                status += " | ⊘ No dasha"
            else:
                status += " | ✓ Dasha"
            
            print(f"[{i:3d}/{len(charts)}] Chart {chart_id:3d} {status}")
            
        except Exception as e:
            error_count += 1
            print(f"[{i:3d}/{len(charts)}] Chart {chart_id:3d} ✗ {str(e)[:50]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"📊 Results:")
    print(f"  ✓ Updated: {updated_count}")
    print(f"  ✗ Errors: {error_count}")
    print(f"{'='*60}\n")
    
    if updated_count > 0:
        print("🔄 Rebuilding analytics cache...", end=' ', flush=True)
        try:
            rebuild_cache()
            print("✓")
        except Exception as e:
            print(f"✗ {str(e)[:60]}")
    
    print("✅ Regeneration complete!")


if __name__ == '__main__':
    regenerate_all_charts()

