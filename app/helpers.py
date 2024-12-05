import json
from app.program import reccPaper

def save_results_to_file(final_results, file_name='combined_results.json'):
    with open(file_name, 'w') as f:
        json.dump(final_results, f)

def load_results_from_file(file_name='combined_results.json'):
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def update_results(new_paper, file_name='combined_results.json', add=True):
    # Load existing results
    final_results = load_results_from_file(file_name)
    
    # Get recommendations for the new paper
    new_results = reccPaper(new_paper)
    
    # Update the existing results
    if add:
        for rec in new_results:
            if rec not in final_results:
                final_results[rec] = 0
            final_results[rec] += 1
    else:
        for rec in new_results:
            final_results[rec] -= 1
            if final_results[rec] == 0:
                del final_results[rec]

    
    # Save the updated results back to the file
    save_results_to_file(final_results, file_name)
    
    # Return the top 10 recommendations
    sorted_results = sorted([(count, rec) for rec, count in final_results.items()], reverse=True)
    return sorted_results[:10]

