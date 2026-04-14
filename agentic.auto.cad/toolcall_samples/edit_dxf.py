import sys
import ezdxf
import os

def edit_existing_dxf(input_filename, output_filename="edited_sample.dxf"):
    input_path = os.path.join("agentic.auto.cad", "processing", input_filename)
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    try:
        doc = ezdxf.readfile(input_path)
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        return
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file.")
        return

    msp = doc.modelspace()
    
    # Query all lines and change their color to Green (3)
    for line in msp.query("LINE"):
        line.dxf.color = 3
        print(f"Changed line color at {line.dxf.start} to Green")

    output_path = os.path.join("agentic.auto.cad", "processing", output_filename)
    doc.saveas(output_path)
    print(f"Edited file saved to {output_path}")

if __name__ == "__main__":
    # Check for config_dunp
    if len(sys.argv) > 1 and sys.argv[1] == "config_dunp":
        print("Running with config_dunp")
    
    # We edit the file created by create_line.py
    edit_existing_dxf("sample_line.dxf")
