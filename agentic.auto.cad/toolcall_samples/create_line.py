import sys
import ezdxf
import os

def create_simple_line(filename="sample_line.dxf"):
    # Create a new DXF document
    doc = ezdxf.new("R2010")
    
    # Create new layer
    doc.layers.add(name="Lines", color=1) # Red
    
    # Add a line to the modelspace
    msp = doc.modelspace()
    msp.add_line((0, 0), (10, 10), dxfattribs={"layer": "Lines"})
    
    # Ensure processing directory exists
    output_path = os.path.join("agentic.auto.cad", "processing", filename)
    doc.saveas(output_path)
    print(f"File saved to {output_path}")

if __name__ == "__main__":
    # Check for config_dunp as per user rules if this were a test
    if len(sys.argv) > 1 and sys.argv[1] == "config_dunp":
        print("Running with config_dunp")
    
    create_simple_line()
