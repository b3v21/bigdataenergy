import { Button } from '@/components/ui/button';
import React from 'react';
import { callAPIPost } from '../simulation/stubbed';


const Settings = () => {
	return <div>Settings
		<br></br>
			<Button onClick={callAPIPost}>send active stations</Button>

	</div>;
};

export default Settings;
