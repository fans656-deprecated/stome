import React from 'react';
import $ from 'jquery';
import { withRouter } from 'react-router-dom';

import Console from './Console';
import UserPanel from './UserPanel';
import Nav from './Nav';
import Content from './Content';
import ItemPanel from './ItemPanel';
import StatusBar from './StatusBar';
import getTree from './node';
import upload from './upload';

import './css/Explorer.css';

class Explorer extends React.Component {
  state = {
    tree: null,
    uploadPath: null,
  }

  componentWillReceiveProps = async (props) => {
    await this.state.tree.setCurrentPath(props.currentPath);
    this.setState({});
  }

  componentDidMount = async () => {
    window.upload = this.upload;
    const tree = await getTree(this.props.rootPath);
    await tree.setCurrentPath(this.props.currentPath);
    window.root = tree.root;
    this.setState({tree: tree});
  }

  render() {
    const tree = this.state.tree;
    if (!tree) return null;
    return (
      <div className="explorer">
        <header className="horizontal">
          <div className="left child">
            <Console/>
          </div>
          <div className="right child">
            <UserPanel/>
          </div>
        </header>
        <main className="horizontal">
          <Nav tree={this.state.tree}
            onNodeClicked={this.onNodeClickedInNav}
            onNodeToggled={this.onNodeToggledInNav}
          />
          <Content dir={this.state.tree.currentDir}
            onClick={this.onItemClickedInContent}
          />
          <ItemPanel node={tree.currentItem || tree.currentDir}/>
        </main>
        <footer>
          <div className="child">
            <StatusBar item={tree.currentItem || tree.currentDir}/>
          </div>
        </footer>
        <div style={{display: 'none'}}>
          <input id="upload"
            type="file"
            multiple
            style={{display: 'none'}}
            onChange={this.onFileInputChange}
          />
        </div>
      </div>
    );
  }

  onNodeClickedInNav = async (node) => {
    console.log(node);
    if (node.isCurrentDir()) {
      await node.toggle();
    } else {
      this.changeCurrentDir(node);
    }
    this.setState({});
  }

  onItemClickedInContent = async (node) => {
    if (node && node.isCurrentItem()) {
      if (node.meta.listable) this.changeCurrentDir(node);
    } else {
      this.state.tree.currentItem = node;
    }
    this.setState({});
  }

  onNodeToggledInNav = () => {
    this.setState({});
  }

  changeCurrentDir = (node) => {
    this.state.tree.setCurrentDir(node);
    this.props.history.push(node.meta.path);
  }

  upload = (path) => {
    this.setState({
      uploadPath: path,
    }, () => $('#upload').click());
  }

  onFileInputChange = () => {
    const fileInput = $('#upload');
    const files = fileInput[0].files;
    let path = this.state.uploadPath;
    let name = null;
    if (!path.startsWith('/')) {
      const curPath = this.state.tree.currentDir.meta.path;
      path = curPath + '/' + path;
    }
    if (!path.endsWith('/')) {
      const parts = path.split('/');
      name = parts.pop();
      path = parts.join('/') + '/';
    }
    if (files.length === 1) {
      this.doUploadFile(path, name, files[0]);
    } else {
      for (let i = 0; i < files.length; ++i) {
        this.doUploadFile(path, null, files[i]);
      }
    }
    fileInput.val(null);
  }

  doUploadFile = (path, name, file) => {
    path = path + (name || file.name);
    upload(path, file);
  }
}

Explorer = withRouter(Explorer);

export default Explorer;
