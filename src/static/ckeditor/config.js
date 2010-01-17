/*
Copyright (c) 2003-2010, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.editorConfig = function( config )
{
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
    config.toolbar = 'Custom';
    config.toolbar_Custom = [
	['Bold', 'Italic', 'Underline', 'Strike', '-', 
	 'Format','Font','FontSize', 'TextColor', '-', 
	 'NumberedList', 'BulletedList', '-', 
	 'Link', 'Unlink','-','Image', 'Flash']];
};
