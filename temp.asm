.align 2
.thumb 

/*Well, this is the source code for the battle bg hack. Pretty simple stuff.
When the battle bg is loaded, the game stores the background number to be loaded in r0.
This hack branches the routine right after that to check the var and if there is something in it,
load that as the new background.

The branches to this routine (BPRE only) need to be done as follows:

0x0800F26C= change "ldr r5, #0x0824EE34" to "ldr r5, #0x08F00001" (or the location you choose to put this routine at.)
0x0800F26E= change "lsl r4,r0,#0x2" to "bx r5"
0x0800F270= change "add r4,r4,r0" to "pop {r5}"

0x0800F2B8= change "ldr r5, #0x0824EE34" to "ldr r5, 0x08F00041" (The location Main2 begins at, +1. It was 0x08F00031 in the patch)
0x0800F2BA= change "lsl r4,r0,#0x2" to "bx r5"
0x0800F2BC= change "add r4,r4,r0" to "pop {r5}"

Now, at 0x0800F320, 0x0800FD5C, and 0x0800FD88 change the pointer (which points to the original bg table [0x0824EE34])
to the new BG table location which is 0x08F10000 in here and the patch.

This source is based off what is in the patch. It is ment to modified so that hackers who have already used 0xF00000+ in their
hacks can have flexibility in the location of the routine.

I haven't tested this routine as it is, but it should work... "Should" being the key word...
The reason being, I was given the routine without the var_loader already in a German Rom and I branched it later
to include the var_loader, so this source code is the all in one.*/



.org 0xF00000
Main:	ldr r5, new_bg_table
		push {r5}
		push {r1}
		bl varloader
		
post_var_loader:	cmp r1,#0x0
		beq return
		mov r0,r1
		
return:	pop {r1}
		ldr r5, return_offset
		lsl r4,r0,#0x2
		add r4,r4,r0
		bx r5
		
varloader:	push {r0, r2}
		ldr r0, var_id
		bl call_decrypt
		ldrh r0, [r0]
		mov r1, r0
		pop {r0,r2}
		bl post_var_loader
		
call_decrypt:	ldr r2, vardecrypt
		bx r2
		
		
.align 2
		
		

var_id: 	.word  0x000040F7
vardecrypt: 	.word  0x0806E455
new_bg_table:	.word	0x08F10000
return_offset:	.word	0x0800F271



.align 2

Main2:	ldr r5, new_bg_table2
		push {r5}
		push {r1}
		bl varloader2
		
post_var_loader2:	cmp r1,#0x0
		beq return2
		mov r0,r1
		
return2:	pop {r1}
		ldr r5, return_offset2
		lsl r4,r0,#0x2
		add r4,r4,r0
		bx r5
		
varloader2:	push {r0, r2}
		ldr r0, var_id2
		bl call_decrypt2
		ldrh r0, [r0]
		mov r1, r0
		pop {r0,r2}
		bl post_var_loader2
		
call_decrypt2:	ldr r2, vardecrypt2
		bx r2
		
.align 2


.var_id2: .word  0x000040F7
vardecrypt2: 	.word  0x0806E455
new_bg_table2:	.word	0x08F10000
return_offset2:	.word	0x0800F2BC
