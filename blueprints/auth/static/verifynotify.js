/*==================================================*
 $Id: verifynotify.js,v 1.1 2003/09/18 02:48:36 pat Exp $
 Copyright 2003 Patrick Fitzgerald
 http://www.barelyfitz.com/webdesign/articles/verify-notify/

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *==================================================*/

function verifynotify(field1, field2, result_id) {
 this.field1 = field1;
 this.field2 = field2;
 this.result_id = result_id;
 this.match_html = "<SPAN STYLE=\"color:green\">Thank you, your passwords match all criteria!<\/SPAN>";
 this.nomatch_html = "<SPAN STYLE=\"color:red\">Please make sure your passwords match.<\/SPAN>";
 this.short_html = "<SPAN STYLE=\"color:red\">Make sure your password is at least 8 characters long.<\/SPAN>";
 this.matches = false;
 this.passlength = false;

 this.canProceed = function() {
	 return this.matches&&this.passlength;
 }
 
 this.check = function() {

   // Make sure we don't cause an error
   // for browsers that do not support getElementById
   if (!this.result_id) { return false; }
   if (!document.getElementById){ return false; }
   r = document.getElementById(this.result_id);
   if (!r){ return false; }

   if(this.field1.value=="" || this.field2.value==""){r.innerHTML = ""; this.matches = false; return false;}
   
   if (this.field1.value != "" && this.field1.value == this.field2.value) {
     r.innerHTML = this.match_html;
     if(this.field1.value.length>=8) {
    	 this.passlength = true;
     } else {
    	 r.innerHTML = this.short_html;
    	 this.passlength = false;
     }
     this.matches = true;
   } else {
     r.innerHTML = this.nomatch_html;
     this.matches = false;
   }
 }
}
