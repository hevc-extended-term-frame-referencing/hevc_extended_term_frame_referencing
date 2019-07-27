% main for scene_cut
[status,ffmpeg_bin,ffprobe_bin,threshold_scene,max_chunks,profile_string]=...
        parser('params.txt');

if status>=0
   [status1] = scene_merge_v2(ffmpeg_bin);
   if status1<0
        fprintf('\nError in the execution of scene merging.\n\n');
   end
else
    fprintf('\nError: params.txt file not parsed correctly.\n\n');
end

