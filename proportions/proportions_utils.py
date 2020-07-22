



def make_dirs(input_dir, folder):
    #XXX neaten this up 

    wdir = os.path.join(input_dir, folder)
    os.chdir(wdir)
    
    # generate output paths
    proc_dir = os.path.join(wdir, 'processing')
    prop_dir = os.path.join(wdir, 'proportions')
    dec_prop_dir = os.path.join(wdir, 'dec_proportions')
    
    # make directories if they don't exist yet
    os.makedirs(proc_dir, exist_ok=True)
    os.makedirs(prop_dir, exist_ok=True)
    os.makedirs(dec_prop_dir, exist_ok=True)
    
    print('directories made', datetime.datetime.now())
    
    return wdir, proc_dir, prop_dir, dec_prop_dir





