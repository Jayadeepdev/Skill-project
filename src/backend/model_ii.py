import os

def generate_results():
    """
    Saves a dummy output file and returns the Hello World text.
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join("data", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Simulate saving a CSV to the output folder
    output_path = os.path.join(output_dir, "results.csv")
    with open(output_path, "w") as f:
        f.write("column1,column2\nhello,world")
        
    text_result = "ANALYSIS COMPLETE:\n\nHello World"
    
    # Return text and None for graphs (UI handles the placeholder slides)
    return text_result, None